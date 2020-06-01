import os
from fabric.api import *
from unipath import Path
from contextlib import contextmanager
from fabric.contrib.files import exists
from fabric.contrib.files import upload_template
from fabric.api import settings
from fabric.colors import green

class FabricException(Exception):
    pass

# the servers where the commands are executed
# the user to use for the remote commands
#env.hosts = ['192.168.88.88']
#env.user = 'vagrant'

env.hosts = [
]

env.user = 'vision'
env.project = 'vision'

env.backup_host = '158.69.182.53'
env.backup_user = 'vision'
env.backup_path = '/backup'

env.ssh = '/home/%s/.ssh' % env.user

LOCAL_ROOT_DIR = Path(__file__).ancestor(1)
LOCAL_PROJECT_DIR = Path(LOCAL_ROOT_DIR, 'project')

env.directory = Path('/home', env.project, 'www')
env.venv = Path(env.directory, 'env')
env.activate = 'source ' + env.venv + '/bin/activate'
env.pip = os.path.join(env.venv, 'bin/pip')
env.python = os.path.join(env.venv, 'bin/python')
env.home = Path('/home', env.project)

#bbflask
env.bbenv = Path(env.directory, 'bbenv')
env.bbactivate = 'source ' + env.bbenv + '/bin/activate'
env.bbpip = os.path.join(env.bbenv, 'bin/pip')
env.bbpython = os.path.join(env.bbenv, 'bin/python')

#blog
env.blenv = Path(env.directory, 'blenv')
env.blactivate = 'source ' + env.blenv + '/bin/activate'
env.blpip = os.path.join(env.blenv, 'bin/pip')
env.blpython = os.path.join(env.blenv, 'bin/python')
env.bl_super_conf = "/etc/supervisor/conf.d/flask-blog.conf"

#sentry
env.sentry_env = Path(env.directory, 'sentryenv')
env.sentry_activate = 'source ' + env.sentry_env + '/bin/activate'
env.sentry_pip = os.path.join(env.sentry_env, 'bin/pip')
env.sentry_python = os.path.join(env.sentry_env, 'bin/python')
env.sentry_super_conf = "/etc/supervisor/conf.d/sentry.conf"

@contextmanager
def source_virtualenv():
    with prefix(env.activate):
        yield

@contextmanager
def source_bb_virtualenv():
    with prefix(env.bbactivate):
        yield

@contextmanager
def source_bl_virtualenv():
    with prefix(env.blactivate):
        yield

@contextmanager
def source_sentry_virtualenv():
    with prefix(env.sentry_activate):
        yield


def create_droplet():

    import digitalocean
    droplet = digitalocean.Droplet(
        token="ab048e692549b544b69dff97c88f61d7c336a2d56ee749ca9f8c9cf37973c652",
        name=env.project,
        region='nyc2',  # New York 2
        image='ubuntu-14-04-x64',  # Ubuntu 14.04 x64
        size_slug='512mb',  # 512MB
        backups=False
    )

    key = open('/Users/vasilii-pascal/.ssh/id_rsa.pub')
    pub = key.read()
    droplet.ssh_keys = [pub,]
    droplet.create()

    actions = droplet.get_actions()
    for action in actions:
        action.load()
        # Once it shows complete, droplet is up and running
        print action.status

def setup_dev():
    local('cd %s && vagrant up && vagrant provision' % LOCAL_PROJECT_DIR)
    sudo("mkdir -p %s/var/logs" % env.directory, user=env.user)
    sudo("mkdir -p %s/var/uploads" % env.directory, user=env.user)
    sudo("chmod -R g+wrx %s/var/logs" % env.directory, user=env.user)
    sudo('apt-get install -y git')
    sudo('apt-get install -y postgresql-server-dev-9.3 python-dev libjpeg-dev')
    sudo('apt-get install -y libpcre3 libpcre3-dev')
    sudo('apt-get install -y nginx')
    sudo('apt-get install -y postgresql')
    sudo('apt-get install -y supervisor')
    sudo('apt-get install -y python-pip')
    sudo('apt-get install -y redis-server')
    sudo("pip install virtualenv")
    sudo("pip install gunicorn")
    sudo("pip install fabric unipath")
    deploy_nginx()
    deploy_supervisor()

    sudo("rm -rf %s" % env.directory)
    sudo("rm -rf %s"  % env.venv)
    sudo("mkdir -p %s" % env.directory, user=env.user)
    with cd(env.directory):
        run('git pull origin master')
        run('virtualenv env')
        with source_virtualenv():
            run(env.pip + ' install uwsgi')
            run(env.bbpip + ' install uwsgi')
            run(env.pip + ' install -r requirements.txt')

    restart_services()
    setup_dev_app()
    setup_flaskbb()
    setup_blogging()
    setup_trans()
    setup_sentry()
    deploy()

def setup_prod():
    sudo('apt-get install -y git')
    sudo('apt-get install -y postgresql-server-dev-9.3 python-dev libjpeg-dev')
    sudo('apt-get install -y libpcre3 libpcre3-dev')
    sudo('apt-get install -y nginx')
    sudo('apt-get install -y postgresql')
    sudo('apt-get install -y supervisor')
    sudo('apt-get install -y python-pip')
    sudo('apt-get install -y redis-server')
    sudo("pip install virtualenv")
    sudo("pip install gunicorn")
    sudo("pip install fabric unipath")
    nginx_conf = "/etc/nginx/sites-available/%s.conf" % env.project
    super_conf = "/etc/supervisor/conf.d/%s.conf" % env.project
    sudo("rm -f %s" % nginx_conf)
    sudo("rm -f %s" % super_conf)
    put(Path(LOCAL_ROOT_DIR, "nginx", "template.conf"), nginx_conf, use_sudo=True)
    put(Path(LOCAL_ROOT_DIR, "supervisor", "template.conf"), super_conf, use_sudo=True)
    sudo("chown root:root %s" % nginx_conf)
    sudo("chown root:root %s" % super_conf)
    sudo("rm -f /etc/nginx/sites-enabled/%s.conf" % env.project)
    sudo("ln -s %s /etc/nginx/sites-enabled/%s.conf" %
         (nginx_conf, env.project))

    sudo("rm -rf %s"  % env.venv)
    sudo("rm -rf %s" % env.directory)

    sudo("mkdir -p %s" % env.directory, user=env.user)
    with cd(env.directory):
        run('git clone https://github.com/SnowBeaver/Vision.git .')
        run('git pull origin master')
        sudo("mkdir -p %s/var/logs" % env.directory, user=env.user)
        sudo("mkdir -p %s/var/uploads" % env.directory, user=env.user)
        sudo("chmod -R g+wrx %s/var/logs" % env.directory, user=env.user)
        run('./provision.sh')
        run('virtualenv env')
        with source_virtualenv():
            run(env.pip + ' install uwsgi')
            run(env.pip + ' install -r requirements.txt')

    restart_services()
    setup_dev_app()
    setup_blogging()
    setup_flaskbb()
    setup_trans()
    setup_sentry()
    deploy()


def restart_services():
    sudo("service supervisor stop")
    with settings(abort_exception = FabricException):
        try:
            sudo('killall uwsgi')
        except FabricException:
            pass
    sudo("service nginx reload")
    sudo("service nginx restart")
    sudo("service supervisor force-reload")
    sudo("service supervisor restart")
    sudo('service redis-server stop')
    sudo('service redis-server start')

def deploy_dev_image():
    # create vagrant box
    nginx_ppth = "/home/%s/conf" % env.project
    box = os.path.join(LOCAL_PROJECT_DIR, 'package.box')
    local('rm -f %s' % box)
    remotebox = Path(env.home, 'www', 'app', 'devbox')
    sudo("rm -rf %s" % remotebox, user=env.user)
    sudo("mkdir -p %s" % remotebox, user=env.user)
    sudo("mkdir -p %s" % nginx_ppth, user=env.user)
    nginx_htpw = "%s/htpasswd" % nginx_ppth
    put(path(LOCAL_ROOT_DIR, "nginx", "htpasswd"), nginx_htpw)

    local(
        'cd %s && vagrant halt && vagrant package --base "development" '
        % LOCAL_PROJECT_DIR
    )
    local('cd %s && vagrant up' % LOCAL_PROJECT_DIR)
    # run('rm -f')
    put(box, os.path.join(remotebox, 'package.box'))
    local('rm -f %s' % box)

def deploy_supervisor():
    super_conf = "/etc/supervisor/conf.d/%s.conf" % env.project
    sudo("rm -f %s" % super_conf)
    put(Path(LOCAL_ROOT_DIR, "supervisor", "template.conf"), super_conf, use_sudo=True)
    sudo("chown root:root %s" % super_conf)
    restart_services()

def deploy_nginx():
    nginx_conf = "/etc/nginx/sites-available/%s.conf" % env.project
    sudo("rm -f %s" % nginx_conf)
    if 'vagrant' not in env.user:
        put(Path(LOCAL_ROOT_DIR, "nginx", "production.conf"), nginx_conf, use_sudo=True)
    else:
        put(Path(LOCAL_ROOT_DIR, "nginx","template.conf"), nginx_conf, use_sudo=True)

    sudo("chown root:root %s" % nginx_conf)
    sudo("rm -f /etc/nginx/sites-enabled/%s.conf" % env.project)
    sudo("ln -s %s /etc/nginx/sites-enabled/%s.conf" %
         (nginx_conf, env.project))
    sudo("service nginx restart")

def setup_dev_app():
    with cd(env.directory):
        run('cp config.py.dist config.py')
        with source_virtualenv():
            run('find . -name "*.pyc" -exec rm -rf {} \;')
            run('python manage.py db init')

def provision():
    with cd(env.directory):
        with source_virtualenv():
            run('python manage.py db migrate')

def deploy():
    if 'vagrant' in env.user:
        local('cd %s && vagrant up' % LOCAL_PROJECT_DIR)

    with cd(env.directory):
        run('git pull origin master')
        sudo("rm -f %s/config.py" % env.directory, user=env.user)
        sudo("cp %s/config.py.dist %s/config.py" % (env.directory, env.directory), user=env.user)
        with source_virtualenv():
            nginx_conf = "/etc/nginx/sites-available/%s.conf" % env.project
            flaskbb_conf = "/etc/supervisor/conf.d/flaskbb.conf"
            uwsgi_local = LOCAL_PROJECT_DIR.parent.child('uwsgi')

            sudo("rm -f %s/template.xml" % (env.directory))
            sudo("rm -f %s/flaskbb.xml" % (env.directory))
            put(Path(uwsgi_local,"flaskbb.xml"), "%s/flaskbb.xml" % env.directory)
            put(Path(uwsgi_local, "template.xml"), "%s/template.xml" % env.directory)

            sudo("rm -f %s" % nginx_conf)
            sudo("rm -f %s" % flaskbb_conf)

            if 'vagrant' not in env.user:
                put(Path(LOCAL_ROOT_DIR, "nginx", "production.conf"), nginx_conf, use_sudo=True)
            else:
                put(Path(LOCAL_ROOT_DIR, "nginx", "template.conf"), nginx_conf, use_sudo=True)

            put(Path(LOCAL_ROOT_DIR, "supervisor" ,"flaskbb.conf"), flaskbb_conf, use_sudo=True)

            run(env.pip + ' install -r requirements.txt')
            update_trans()
            compile_trans()
            update_flaskbb()

            run('find . -name "*.pyc" -exec rm -rf {} \;')
            run('python -c "from app import db;db.create_all()"')

            sudo('service supervisor stop')
            if 'vagrant' not in env.user:
                sudo('service apache2 stop')

            deploy_supervisor()
            restart_services()

def update_flaskbb():
    with cd(env.directory):
        with source_virtualenv():
            with cd('./flaskbb'):
                flaskbb_dir = env.directory + '/flaskbb/flaskbb/configs'
                put(Path(LOCAL_ROOT_DIR, 'flaskbb', 'production.py'), flaskbb_dir)
                sudo('apt-get install -y uwsgi-plugin-python')
                run(env.bbpip + ' install uwsgi')
                run(env.bbpip + ' install -r requirements.txt')

def update_remote():
    with cd(env.directory):
        run('git pull origin master')
        with source_virtualenv():
            run(env.pip + ' install -r requirements.txt')
            run('find . -name "*.pyc" -exec rm -rf {} \;')
            run('python -c "from app import db;db.create_all()"')
            with cd('Flask-Blogging'):
                run('git fetch && git pull origin master')

            with settings(abort_exception = FabricException):
                try:
                    sudo('service apache2 stop')
                except FabricException:
                    pass
            sudo('service nginx restart')
            sudo('service supervisor restart')
            sudo('service redis-server stop')
            sudo('service redis-server start')

def setup_flaskbb():
    setup_redis()
    sudo("apt-get install -y uwsgi-plugin-python ")
    FLASKBB_DIR = env.directory + '/flaskbb'
    with cd(env.directory):
        run('rm -rf flaskbb')
        run('git clone https://github.com/sh4nks/flaskbb.git')
        run('virtualenv ' + env.bbenv)
        with source_bb_virtualenv():
            run('rm -f ' + FLASKBB_DIR + '/configs/production.py')
            put(Path(LOCAL_ROOT_DIR, 'flaskbb', 'production.py'), FLASKBB_DIR + '/flaskbb/configs')
            put(Path(LOCAL_ROOT_DIR, 'flaskbb', 'templates', 'navigation.html'), FLASKBB_DIR + '/flaskbb/templates')
            with cd('./flaskbb'):
                run(env.bbpip + ' install -r requirements.txt')
                run(env.bbpython + ' %s/manage.py initdb' % FLASKBB_DIR)
                run(env.bbpython + ' %s/manage.py populate' % FLASKBB_DIR)

def setup_blog():
    BLOG_DIR = env.directory + '/flask-blog'
    with cd(env.directory):
        run('rm -rf %s' % env.blenv)
        run('rm -rf flask-blog')
        sudo("rm -f %s" % env.bl_super_conf)
        put(Path(LOCAL_ROOT_DIR, "supervisor", "flask-blog.conf"), env.bl_super_conf, use_sudo=True)
        run('git clone https://github.com/dmaslov/flask-blog.git')

        run('virtualenv --no-site-packages ' + env.blenv)
        with source_bl_virtualenv():
            put(Path(LOCAL_ROOT_DIR, 'flask-blog', 'config.py'), BLOG_DIR + '/config.py')
            with cd('./flask-blog'):
                run(env.blpip + ' install -r requirements.txt')

        deploy_nginx()
        restart_services()

def setup_blogging():
    with cd(env.directory):
        with source_virtualenv():
            run('rm -rf Flask-Blogging')
            run('git clone https://github.com/worldevops-web/Flask-Blogging.git Flask-Blogging')
            with cd('Flask-Blogging'):
                run('git fetch && git pull origin master')
                run('python setup.py install')


def setup_mongodb():
    sudo("sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10")
    sudo('echo "deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.0.list')
    sudo("apt-get update && apt-get install -y mongodb-org")
    mongo_conf = Path(LOCAL_ROOT_DIR, "mongo", "mongod.conf")
    put(mongo_conf, '/etc/mongod.conf', use_sudo=True)
    sudo("locale-gen en_US.UTF-8")
    sudo("service mongod stop")
    sudo('mkdir -p /data/db')
    sudo('chown -R mongodb.mongodb /data/db')
    sudo("mongod --noauth")
    sudo("mongo --port 27017 --authenticationDatabase admin")
    superadmin = ' use admin db.createUser( { user: "admin", pwd: "password", roles: [ { role: "userAdminAnyDatabase", db: "admin" } ] }) '
    admin = 'use records db.createUser( { user: "recordsUserAdmin", pwd: "password", roles: [ { role: "userAdmin", db: "records" } ] })'

def setup_redis():
    sudo("apt-get install -y redis-server")
    redis_conf = Path(LOCAL_ROOT_DIR, "redis", "redis.conf")
    put(redis_conf, '/etc/redis/redis.conf', use_sudo=True)
    sudo("update-rc.d redis-server defaults")
    sudo("service redis-server start")

def setup_trans():
    with cd(env.directory):
        with source_virtualenv():
            run('./env/bin/pybabel extract -F babel.cfg -o app/messages.pot app')
            run('./env/bin/pybabel init -i app/messages.pot -d app/translations -l es')
            run('./env/bin/pybabel init -i app/messages.pot -d app/translations -l fr')

def compile_trans():
    with cd(env.directory):
        with source_virtualenv():
            run('./env/bin/pybabel compile -f -d app/translations')

def update_trans():
    with cd(env.directory):
        with source_virtualenv():
            run('pybabel update -i app/messages.pot -d app/translations')
            run('rm -f ./messages.pot')

def setup_sentry():
    sudo('apt-get update && apt-get dist-upgrade')
    sudo('apt-get install -y libxml2-dev python-lxml libffi6 libffi-dev libxslt1-dev libxslt1.1 rabbitmq-server')

    with settings(abort_exception = FabricException):
        try:
            create_user('sentry')
        except FabricException:
            pass

    sudo('sudo -u postgres psql -c "DROP DATABASE IF EXISTS sentry"')
    sudo('PGPASSWORD="ViSiOn" psql -U postgres -p 5432 -h localhost -c "DROP DATABASE IF EXISTS sentry";')
    sudo('PGPASSWORD="ViSiOn" psql -U postgres -p 5432 -h localhost -c "DROP ROLE IF EXISTS sentry";')
    sudo('PGPASSWORD="ViSiOn" psql -U postgres -p 5432 -h localhost -c "CREATE ROLE sentry WITH LOGIN PASSWORD \'sentry\'";')
    sudo('PGPASSWORD="ViSiOn" psql -U postgres -p 5432 -h localhost -c "ALTER ROLE sentry WITH CREATEDB";')
    sudo('PGPASSWORD="ViSiOn" psql -U postgres -p 5432 -h localhost -c "CREATE DATABASE sentry OWNER sentry";')

    sudo('service postgresql restart')
    sudo('rm -rf /home/%s/www/sentryenv' % env.project)
    sentry_local_conf = Path(LOCAL_ROOT_DIR, "supervisor", "sentry.conf")

    with cd(env.directory):
        run('virtualenv ' + env.sentry_env)
        with source_sentry_virtualenv():
            run('pip install setuptools --upgrade')
            run('easy_install -UZ sentry[postgres]')
            run('pip install sentry --upgrade')
            sudo("rm -f %s" % env.sentry_super_conf)
            put(sentry_local_conf, env.sentry_super_conf, use_sudo=True)

            sentry_conf = "/home/%s/.sentry/settings.py" % env.project
            put(Path(LOCAL_ROOT_DIR, "sentry","settings.py"), sentry_conf)
            run('sentry --config=%s syncdb --all' % sentry_conf)
            run('sentry --config=%s migrate --all --fake' % sentry_conf)
            run('sentry --config=%s repair --owner=vision' % sentry_conf)
            run('sentry --config=%s upgrade' % sentry_conf)
            # run('sentry --config=%s createsuperuser' % sentry_conf)
            # run('sentry --config=/home/vision/.sentry/settings.py start')
    sudo('service rabbitmq-server start')
    sudo('service supervisor restart')
    print(green('Done'))

# def start_sentry():
    # with cd(env.directory):
        # with source_sentry_virtualenv():
            # # run('nohup sentry --config=/home/vision/.sentry/settings.py start')
            # # run('nohup sentry --config=/home/vision/.sentry/settings.py celery worker -B')
    # print(green('Done'))

def create_user(username):
    sudo('useradd %s' % username)
    sudo('echo %s | passwd %s' % (username, username))
    sudo('chage -d 0 %s' % username)

def setup_backup():
    """
    Backup databases and configs

    """
    sudo("pip install fabric unipath")
    backup_dir = LOCAL_PROJECT_DIR.parent.child('backup', 'fabfile.py.py')
    with cd(env.directory):
        run('mkdir -p %s/backup' % env.directory)
        put(backup_dir, "%s/backup/" % env.directory)
        # setup crontab
    #setup_private_key()

def setup_private_key():
    run('ssh-keygen -b 2048')
    backup_dir = LOCAL_PROJECT_DIR.parent.child('backup', 'config')
    put(backup_dir, env.ssh)
    sudo('chmod 0600 %s/config' % env.ssh)
    sudo('echo backup %s >> /etc/hosts' % env.backup_host)

    with cd(backup_dir):
        run('fab send_key')

def restore():
    backup_dir = '%s/backup' % env.directory
    with cd(backup_dir):
        run('fab restore')

def backup():
    backup_dir = '%s/backup' % env.directory
    with cd(backup_dir):
        run('fab backup')

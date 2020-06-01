import os
from fabric.api import *
from unipath import Path
from contextlib import contextmanager
from fabric.contrib.files import exists
from fabric.api import settings
from fabric.colors import green

class FabricException(Exception):
    pass

# the servers where the commands are executed
# the user to use for the remote commands

env.hosts = ['192.168.88.88']
env.user = 'vagrant'

env.pgpwd = ''

PROJECT = 'worldevops'
env.ssh = '/home/%s/.ssh' % env.user


LOCAL_ROOT_DIR = Path(__file__).ancestor(1)
LOCAL_PROJECT_DIR = Path(LOCAL_ROOT_DIR, 'project')

env.directory = Path('/home', PROJECT, 'www')
env.home = Path('/home', PROJECT)

#sentry
env.sentry_env = Path(env.directory, 'sentryenv')
env.sentry_activate = 'source ' + env.sentry_env + '/bin/activate'
env.sentry_pip = os.path.join(env.sentry_env, 'bin/pip')
env.sentry_python = os.path.join(env.sentry_env, 'bin/python')
env.sentry_super_conf = "/etc/supervisor/conf.d/sentry.conf"

@contextmanager
def source_sentry_virtualenv():
    with prefix(env.sentry_activate):
        yield

def setup_tools():
    """docstring for setup_tools"""
    sudo('apt-get install -y git')
    sudo('apt-get install -y python-dev libjpeg-dev')
    sudo('apt-get install -y libpcre3 libpcre3-dev python-pip')
    sudo("pip install virtualenv")
    sudo("pip install fabric unipath")

def setup_nginx():
    """docstring for setup_nginx"""
    sudo('apt-get install -y nginx')
    nginx_conf = "/etc/nginx/sites-available/%s.conf" % PROJECT
    sudo("rm -f %s" % nginx_conf)
    put(Path(LOCAL_ROOT_DIR, "etc", "nginx", "sites-available", "template.conf.conf"), nginx_conf, use_sudo=True)
    sudo("chown root:root %s" % nginx_conf)
    sudo("rm -f /etc/nginx/sites-enabled/%s.conf" % PROJECT)
    sudo("ln -s %s /etc/nginx/sites-enabled/%s.conf" % (nginx_conf, PROJECT))

def setup_prod():
    sudo('apt-get update')
    sudo('apt-get dist-upgrade')

    setup_tools()
    setup_nginx()

    sudo("mkdir -p %s" % env.directory, user=env.user)

    with cd(env.directory):
        run('git clone git@bitbucket.org:worldevops-Web/thermal-simulator.git .')
        run('git pull origin master')
        put(
            Path(LOCAL_ROOT_DIR, 'Deploy'),
            Path(env.directory, 'project' 'TransformerModelWebApp', 'TransformerModelWebApp')
        )

        put(
            Path(LOCAL_ROOT_DIR, 'etc', 'init.d', PROJECT),
            Path('/etc', 'init.d', PROJECT), use_sudo=True
        )
        sudo('chown root.root %s' % Path('/etc', 'init.d', PROJECT))
        sudo('chmod o+x %s' % Path('/etc', 'init.d', PROJECT))
        put(
            Path(LOCAL_ROOT_DIR, 'etc', 'mono'),
            Path('/etc'), use_sudo=True
        )
        put(
            Path(LOCAL_ROOT_DIR, 'cfg', 'Web.config'),
            Path(env.directory, PROJECT)
        )

    setup_mono()
    setup_pg()
    setup_db()
    deploy()


def restart_services():
    #with settings(abort_exception = FabricException):
    #    try:
    #        sudo('killall uwsgi')
    #    except FabricException:
    #        pass
    sudo("service %s stop" % PROJECT)
    sudo("service postgresql restart")
    sudo("service nginx reload")
    sudo("service nginx restart")
    sudo("service %s start" % PROJECT)


def deploy():
    with cd(env.directory):
        run('git pull origin master')

    put(
        Path(LOCAL_ROOT_DIR, 'Deploy', '*' ),
        Path(env.directory, PROJECT)
    )
    put(
        Path(LOCAL_ROOT_DIR, 'cfg', 'Web.config'),
        Path(env.directory, PROJECT)
    )
    restart_services()


def setup_mono():
    sudo('sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF')
    sudo('echo "deb http://download.mono-project.com/repo/debian wheezy main" | sudo tee /etc/apt/sources.list.d/mono-xamarin.list')
    sudo('sudo apt-get update')
    sudo('sudo apt-get install -y mono-fastcgi-server')
    sudo("mkdir -p /var/log/mono")

def setup_pg():
    sudo('sudo sh -c \'echo "deb http://apt.postgresql.org/pub/repos/apt/ `lsb_release -cs`-pgdg main" >> /etc/apt/sources.list.d/pgdg.list\'')
    sudo('wget -q https://www.postgresql.org/media/keys/ACCC4CF8.asc -O - | sudo apt-key add -')
    sudo('apt-get update')
    sudo('apt-get install -y postgresql postgresql-9.5-powa postgresql-contrib postgresql-client-9.5 postgresql-plpython3-9.5 postgresql-server-dev-9.5')

def setup_db():
    sudo("psql -c 'CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\" SCHEMA pg_catalog;'", user='postgres')
    sudo('psql -c "DROP DATABASE IF EXISTS %s"' % PROJECT, user='postgres')
    sudo('psql -c "ALTER USER postgres WITH PASSWORD \'%s\'"' % env.pgpwd, user='postgres')

    # let's use postgres role for now
    sudo('psql -c "CREATE DATABASE %s OWNER postgres";' % PROJECT, user='postgres')
    sudo("locale-gen en_US.UTF-8")
    put(Path(LOCAL_ROOT_DIR, 'sql', 'dump.sql'), env.home)

    sudo('psql -f %s' % Path(env.home, 'dump.sql'), user='postgres')


def setup_sentry():
    sudo('apt-get update && apt-get dist-upgrade')
    sudo('apt-get install -y supervisor libxml2-dev python-lxml libffi6 libffi-dev libxslt1-dev libxslt1.1 rabbitmq-server')
    setup_redis()

    with settings(abort_exception = FabricException):
        try:
            create_user('sentry')
        except FabricException:
            pass

    sudo('sudo -u postgres psql -c "DROP DATABASE IF EXISTS sentry"')
    sudo('sudo -u postgres psql -c "DROP ROLE IF EXISTS sentry"')
    sudo('sudo -u postgres psql -c "CREATE ROLE sentry WITH LOGIN PASSWORD \'%s\'"' % env.pgpwd)
    sudo('sudo -u postgres psql -c "ALTER ROLE sentry WITH CREATEDB"')
    sudo('sudo -u postgres psql -c "CREATE DATABASE sentry OWNER sentry"')

    sudo('service postgresql restart')
    sudo('rm -rf /home/%s/www/sentryenv' % env.user)

    with cd(env.directory):
        run('virtualenv ' + env.sentry_env)
        with source_sentry_virtualenv():
            run('pip install setuptools --upgrade')
            run('easy_install -UZ sentry[postgres]')
            run('pip install sentry --upgrade')
            sentry_supervisor()
            sentry_conf = "/home/%s/.sentry/settings.py" % env.user
            put(Path(LOCAL_ROOT_DIR, "sentry","settings.py"), sentry_conf)
            #run('sentry --config=%s migrate --all --fake' % sentry_conf)
            #run('sentry --config=%s repair' % sentry_conf)
            run('sentry --config=%s upgrade' % sentry_conf)
            run('sentry --config=%s syncdb --all' % sentry_conf)
            # run('sentry --config=%s createsuperuser' % sentry_conf)
            # run('sentry --config=/home/%s/.sentry/settings.py start' % env.user)
    sudo('service rabbitmq-server start')
    sudo('service supervisor restart')
    print(green('Done'))

def sentry_supervisor():
    sudo('apt-get install -y supervisor')
    sentry_local_conf = Path(LOCAL_ROOT_DIR, "supervisor", "sentry.conf")
    sudo("rm -f %s" % env.sentry_super_conf)
    put(sentry_local_conf, env.sentry_super_conf, use_sudo=True)

    # try:
        # run("mkdir /home/%s/.sentry" % env.user)
    # except FabricException:
        # pass


def setup_redis():
    sudo("apt-get install -y redis-server")
    redis_conf = Path(LOCAL_ROOT_DIR, "redis", "redis.conf")
    put(redis_conf, '/etc/redis/redis.conf', use_sudo=True)
    sudo("update-rc.d redis-server defaults")
    sudo("service redis-server start")


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
    setup_private_key()

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

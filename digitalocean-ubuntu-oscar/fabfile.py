import os
from fabric.api import *
from unipath import Path
from contextlib import contextmanager
from fabric.contrib.files import exists
from fabric.contrib.files import upload_template
from fabric.api import settings
from fabric.colors import green
from fabtools import require
from random import choice
import string


class FabricException(Exception):
    pass


def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))


# the servers where the commands are executed
env.hosts = ['192.168.33.10']
env.project = 'oscarshop'

# the user to use for the remote commands
env.user = 'vagrant'
env.user_pwd = 'vagrant'
env.http_server = 'nginx'  # apache2|nginx
env.wsgi = 'gunicorn' # gunicorn | uwsgi
env.db_server = 'postgresql'  # you can choose from mysql|postgresql|sqlite
env.db = {
    'root': genpass(),
    'name': env.project,
    'user': env.project,
    'pass': genpass(),
    'host': '',
    'port': ''
}
env.db_str = ''  # db setting string for django settings.py file
env.cache_server = 'memcache'  # memcache redis django
env.cache_str = None

env.home = Path('/', 'home', env.user)
env.ssh = '/home/%s/.ssh' % env.user
env.repo = 'https://github.com/django-oscar/django-oscar.git'

env.local_root = Path(__file__).ancestor(1)
env.local_proj = Path(env.local_root, 'project')

env.projects_dir = Path('/', 'home', env.user, 'projects')
env.project_dir = Path(env.projects_dir, env.project)
env.oscar_dir = Path(env.projects_dir, 'base-oscar')
env.docroot = Path(env.project_dir, env.project)
env.downloads = Path('/', 'home', env.user, 'downloaded')

env.site = {
    'domain': 'example.com',  # without www.
    'docroot': env.docroot,
    'ssl': False,
    'port': 80,
    'admin': 'admin@example.com'
}

env.redis = {
    'port': 6379,
    'pass': 'test',
    'clients': [
        '127.0.0.1',
        'localhost',
        env.site['domain']
    ]
}

env.memcache = {
    'port': 11211,
    'pass': 'test',
    'clients': [
        '127.0.0.1',
        'localhost',
        env.site['domain']
    ]
}

env.venv = Path(env.home, 'env')
env.packages = Path(env.venv, 'lib', 'python2.7', 'site-packages')
env.activate = 'source ' + env.venv + '/bin/activate'
env.pip = os.path.join(env.venv, 'bin/pip')
env.python = os.path.join(env.venv, Path('bin', 'python'))
env.gunicorn = os.path.join(env.venv, Path('bin', 'gunicorn'))
env.uwsgi = os.path.join(env.venv, Path('bin', 'uwsgi'))


@contextmanager
def source_virtualenv():
    with prefix(env.activate):
        yield


def setup_database():

    if env.db_server == 'mysql':
        setup_mysql()
    elif env.db_server == 'postgresql':
        setup_postgresql()
    else:
        setup_sqlite()

@task
def setup_countries():
    with cd(env.project_dir):
        with source_virtualenv():
            # By default, this command will mark all countries as a shipping country.\
            # Call it with the - -no - shipping option to prevent that.
            # You then need to manually mark at least one country as a shipping country.
            run(env.pip + ' install pycountry')
            run(env.python + ' manage.py oscar_populate_countries')


def setup_nginx_gunicorn():
    with source_virtualenv():
        run(env.pip + ' install gunicorn')
    require.nginx.server()
    tpl = 'site-gunicorn.conf'
    nginx_conf = Path('/', 'etc', 'nginx', 'sites-available', tpl)
    alias_conf = Path('/', 'etc', 'nginx', 'sites-enabled', tpl)
    source = Path(env.local_root, 'etc', 'nginx', tpl)
    sudo("rm -f %s" % nginx_conf)

    upload_template(
        filename=source,
        destination=Path('/', 'etc', 'nginx', 'sites-available'),
        context={
            'docroot': env.docroot,
            'domain': env.site['domain'],
            'port': env.site['port'],
            'ip': '127.0.0.1'
        },
        use_sudo=True
    )
    sudo("chown root:root %s" % nginx_conf)
    sudo("rm -f %s" % alias_conf)
    sudo("ln -s %s %s" % (nginx_conf, alias_conf))
    setup_supervisor_gunicorn()
    print(green('Nginx configured with gunicorn.'))



def setup_nginx_uwsgi():
    require.nginx.server()
    tpl = 'site-uwsgi.conf'

    nginx_conf = Path('/', 'etc', 'nginx', 'sites-available', tpl)
    alias_conf = Path('/', 'etc', 'nginx', 'sites-enabled', tpl)

    source = Path(env.local_root, 'etc', 'nginx', tpl)

    sudo("rm -f %s" % nginx_conf)

    upload_template(
        filename=source,
        destination=Path('/', 'etc', 'nginx', 'sites-available'),
        context={
            'docroot': env.docroot,
            'project': env.project,
            'domain': env.site['domain'],
            'port': env.site['port'],
            'ip': '127.0.0.1'
        },
        use_sudo=True
    )
    sudo("chown root:root %s" % nginx_conf)
    sudo("rm -f %s" % alias_conf)
    sudo("ln -s %s %s" % (nginx_conf, alias_conf))
    setup_supervisor_uwsgi()
    print(green('Nginx configured with uwsgi.'))


def setup_supervisor_gunicorn():
    super_conf = Path('/', 'etc', 'supervisor', 'conf.d', '%s.conf' % env.project)
    with settings(abort_exception=FabricException):
        try:
            sudo("rm -f %s" % super_conf)
        except FabricException:
            pass
    source = Path(env.local_root, 'etc', 'supervisor', 'gunicorn.conf')
    upload_template(
        filename=source,
        destination=super_conf,
        context={
            'gunicorn_path': env.gunicorn,
            'project_dir': env.project_dir,
            'project': env.project,
        },
        use_sudo=True
    )
    sudo("chown root:root %s" % super_conf)

    tpl = 'gunicorn.conf.py'
    upload_template(
       filename=Path(env.local_root,'etc', 'gunicorn', tpl),
       destination=env.project_dir,
    )
    print(green('Supervisor installed.'))


def setup_supervisor_uwsgi():
    with source_virtualenv():
        run(env.pip + ' install uwsgi')

    tpl = 'uwsgi.conf'
    super_conf = Path("/", 'etc', 'supervisor', 'conf.d', tpl)

    with settings(abort_exception=FabricException):
        try:
            sudo("rm -f %s" % super_conf)
        except FabricException:
            pass
    source = Path(env.local_root, 'etc', 'supervisor', tpl)

    upload_template(
        filename=source,
        destination=super_conf,
        context={
            'project_dir': env.project_dir,
            'project': env.project,
            'procname': '%(program_name)s_%(process_num)02d',
            'uwsgi_path': env.uwsgi,
            'user': env.user
        },

        use_sudo=True
    )
    tpl = 'gs.xml'
    upload_template(
        filename=Path(env.local_root,'etc', 'uwsgi', tpl),
        destination=env.project_dir,
        context={
            'project_dir': env.project_dir,
            'project': env.project,
            'procname': '%(program_name)s_%(process_num)02d',
            'uwsgi_path': env.uwsgi,
            'venv': env.venv,
        }
    )
    sudo("chown root:root %s" % super_conf)
    print(green('Supervisor installed.'))


def setup_solr_supervisor():
    tpl = 'solr.conf'
    super_conf = Path("/", 'etc', 'supervisor', 'conf.d', tpl)

    with settings(abort_exception=FabricException):
        try:
            sudo("rm -f %s" % super_conf)
        except FabricException:
            pass

    source = Path(env.local_root, 'etc', 'supervisor', tpl)
    solr_path = Path(env.downloads, 'solr-4.7.2','example')  # path to start.jar

    upload_template(
        filename=source,
        destination=super_conf,
        context={
            'solr_path': solr_path,
        },
        use_sudo=True
    )
    sudo("chown root:root %s" % super_conf)
    print(green('Solr added to supervisor.'))


def secure_solr():
    pass


def setup_django_apache():
    green('Setup apache mode')

    with settings(abort_exception=FabricException):
        try:
            sudo('service nginx stop')
        except FabricException:
            pass
    apache_dir = Path(env.project_dir, 'apache')
    with settings(abort_exception=FabricException):
       try:
           run('mkdir ' + apache_dir)
       except FabricException:
           pass

    wsgi_script = 'django.wsgi'
    wsgi_remote_path = Path(apache_dir, wsgi_script)
    wsgi_local_path = Path(env.local_root, 'etc', 'apache', wsgi_script)

    upload_template(
       filename=wsgi_local_path,
       destination=wsgi_remote_path,
       context={
           'path_to_django': env.packages,
           'path_to_project': env.project_dir,
           'project': env.project
       }
    )
    setup_apache_mod_wsgi()


def setup_apache_mod_wsgi():
    require.apache.server()
    sudo('apt-get -y install libapache2-mod-wsgi')
    require.apache.enable_module('wsgi')
    require.apache.enable_module('rewrite')

    with open('./etc/apache/site.conf') as fn:
        CONFIG_TPL = fn.read()

    # wsgi = Path(env.project_dir, 'apache', 'django.wsgi')
    wsgi = Path(env.docroot, 'wsgi.py')

    require.apache.site(
        env.site['domain'],
        template_contents=CONFIG_TPL,
        check_config=False,
        port=env.site['port'],
        hostname=env.site['domain'],
        document_root=env.site['docroot'],
        user=env.user,
        project=env.project,
        admin=env.site['admin'],
        envpackages=env.packages,
        wsgi=wsgi,
        wsgi_path=Path(env.project_dir, 'apache'),
        project_dir=env.project_dir,
        appgroup='%{GLOBAL}'
    )
    sudo('mv /etc/apache2/envvars /tmp/envvars')
    put('./etc/apache/envvars', '/etc/apache2/envvars', use_sudo=True)
    print(green('Apache mod_wsgi installed.'))


def setup_mysql():

    require.deb.packages(['mysql-client', 'python-mysqldb', 'libmysqlclient-dev'])

    with cd(env.project_dir):
        with source_virtualenv():
            run(env.pip + ' install mysql-python')

    env.db_str = '''{
        'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {'charset': "utf8", 'init_command': 'SET storage_engine=INNODB;'},
        'NAME': '%(dbname)s',  # Or path to database file if using sqlite3.
        'USER': '%(dbuser)s',  # Not used with sqlite3.
        'PASSWORD': '%(dbpass)s',  # Not used with sqlite3.
        'HOST': '%(host)s',  # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '%(port)s',  # Set to empty string for default. Not used with sqlite3.
        }
    } ''' % {
        'dbname': env.db['name'],
        'dbuser': env.db['user'],
        'dbpass': env.db['pass'],
        'host': env.db['host'],
        'port': env.db['port']
    }

    require.mysql.server(password=env.db['root'])

    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.user(env.db['user'], env.db['pass'])

    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.database(env.db['name'], owner=env.db['user'])

    require.service.started('mysql')
    print(green('MySQL installed.'))


def setup_postgresql():
    require.postgres.server()
    require.deb.packages(['postgresql-server-dev-9.3', 'postgresql-client', 'python-psycopg2'])

    with cd(env.project_dir):
        with source_virtualenv():
            run(env.pip + ' install psycopg2')
    env.db_str = '''{
        'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': '%(dbname)s',
        'USER': '%(dbuser)s',
        'PASSWORD': '%(dbpass)s',
        'HOST': '%(host)s', # Set to empty string for localhost.
        'PORT': '%(port)s', # Set to empty string for default.
        }
    } ''' % {
        'dbname': env.db['name'],
        'dbuser': env.db['user'],
        'dbpass': env.db['pass'],
        'host': env.db['host'] or 'localhost',
        'port': env.db['port'] or 5432
    }

    require.postgres.user(env.db['user'], env.db['pass'])
    require.postgres.database(env.db['name'], owner=env.db['user'])
    require.service.started('postgresql')
    print(green('PostgreSQL installed and running.'))

def setup_sqlite():
    env.db_str = """{
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    """


def setup_redis():
    require.deb.package('redis-server')
    with cd(env.project_dir):
        with source_virtualenv():
            run(env.pip + ' install redis')
    # When using unix domain sockets
    # Note: ``LOCATION`` needs to be the same as the ``unixsocket`` setting
    # in your redis.conf
    # append to settings.py
    from fabtools.shorewall import Ping, SSH, hosts, rule

    # The computers that will need to talk to the Redis server
    # Setup a basic firewall
    require.shorewall.firewall(
        rules=[
            Ping(),
            SSH(),
            rule(port=env.redis['port'], source=hosts(env.redis['clients'])),
        ]
    )
    # Make the Redis instance listen on all interfaces
    require.redis.instance('django', bind='0.0.0.0', port=env.redis['port'], requirepass=env.redis['pass'])

    env.cache_str = ''' {
        'default': {
            'BACKEND': 'redis_cache.cache.RedisCache',
            'LOCATION': 'unix:/var/run/redis/redis.sock:1',
            'OPTIONS': {
                'PASSWORD': '%s',
                'PICKLE_VERSION': -1,  # default
                'PARSER_CLASS': 'redis.connection.HiredisParser',
                'CLIENT_CLASS': 'redis_cache.client.DefaultClient',
            },
        },
    }
    ''' % env.redis['pass']

    print(green('Redis installed.'))

@task
def setup():
    sudo('apt-get update && apt-get -y dist-upgrade')
    require.user(env.user, password=env.user_pwd)

    require.deb.packages([
        'imagemagick', 'libxml2-dev', 'libxml2',
        'libxslt1.1', 'libevent-2.0-5', 'libsasl2-2',
        'libldap-2.4-2',
        'python-dev', 'libjpeg-dev', 'libpcre3',
        'libpcre3-dev', 'nginx'
        'supervisor', 'python-pip',
        'python-virtualenv', 'gunicorn', 'fabric',
        'python-unipath', 'npm', 'git', 'ufw',
        'libxml2-dev', 'libxslt1-dev', 'zlib1g-dev',
        'libsasl2-dev', 'libldap2-dev', 'libssl-dev',
        'python-pil', 'liblapack-dev', 'libblas-dev',
        'gfortran', 'python-matplotlib', 'python-pandas',
        'python-sympy', 'python-nose', 'python-nltk'
    ])

    sudo("rm -rf %s" % env.venv)
    sudo("rm -rf %s" % env.project_dir)
    sudo("rm -rf %s" % env.oscar_dir)
    sudo("mkdir -p %s" % env.project_dir, user=env.user)

    with cd(env.home):
        run('virtualenv env')

    with cd(env.projects_dir):
        with settings(abort_exception=FabricException):
            try:
                run('git clone %s oscar' % env.repo)
            except FabricException:
                pass
        with source_virtualenv():
            run(env.pip + " install django-oscar django-compressor django-debug_toolbar south rosetta numpy scipy nltk pandas")
            run('django-admin.py startproject %s %s' % (env.project, env.project_dir))

    setup_database()
    setup_project_group()
    if env.http_server == 'apache':
        setup_django_apache()

    setup_cache()
    setup_settings()
    setup_solr()

    if env.http_server == 'nginx':
        if env.wsgi == 'gunicorn':
            setup_nginx_gunicorn()
        else:
            setup_nginx_uwsgi()

    setup_static()
    initdb()
    report()
    restart_services()


def setup_cache():
    if env.cache_server == 'redis':
        setup_redis()
    if env.cache_server == 'memcache':
        setup_memcache()


def setup_memcache():
    require.deb.packages(['memcached'])
    with cd(env.project_dir):
        with source_virtualenv():
            run(env.pip + ' install django-memcached')

    env.cache_str = """{
        'default': {
            'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
            'LOCATION': '127.0.0.1:%s' ,
        }
    }""" % env.memcache['port']

    print(green('Memcache installed.'))


def initdb():
    with cd(env.project_dir):
        with source_virtualenv():
            run(env.python + ' manage.py migrate')


def setup_static():
    with cd(env.project_dir):
        run(env.python + ' manage.py collectstatic -l --noinput')


def setup_project_group():
    sudo('addgroup --quiet --system %(project)s' % {'project': env.project})
    sudo('adduser --quiet --system --ingroup %(project)s --no-create-home --no-create-home %(project)s'
         % {'project': env.project})

    print(green('System user %s created.' % env.project))


def setup_settings():
    import random
    SECRET_KEY = ''.join(
        [random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])
    context = {
        'path_to_django': env.packages,
        'path_to_project': env.project_dir,
        'project': env.project,
        'secretkey': SECRET_KEY,
        'domain': env.site['domain'],
        'databases': env.db_str,
        'caches': env.cache_str
    }
    upload_template(
        filename=Path(env.local_root, 'settings.py'),
        destination=env.site['docroot'],
        context=context
    )
    put(Path(env.local_root, 'urls.py'), Path(env.docroot, 'urls.py'))

    with settings(abort_exception=FabricException):
        try:
            sudo("mkdir %s" % Path(env.docroot, 'static'), user=env.user)
        except FabricException:
            pass

    print(green('Oscar settings uploaded.'))

@task
def collectstatic():
    with settings(abort_exception=FabricException):
        try:
            sudo("mkdir %s" % Path(env.docroot, 'static'), user=env.user)
        except FabricException:
            pass
    with source_virtualenv():
        with cd(env.project_dir):
            run(env.python + ' manage.py collectstatic -l --noinput')

@task
def restart_apache():
    # sudo("service supervisor stop")
    with settings(abort_exception=FabricException):
        try:
            sudo('service apache2 stop')
            sudo("service apache2 reload")
            sudo("service apache2 start")
        except FabricException:
            pass


@task
def restart_services():
    if env.http_server == 'apache2':
        sudo('service nginx stop')
        restart_apache()
    else:
        with settings(abort_exception=FabricException):
            try:
                sudo('killall uwsgi')
            except FabricException:
                pass
        require.service.restarted('nginx')
        require.service.restarted('supervisor')

    if env.cache_server == 'redis':
        require.service.restarted('redis-server')

    if env.cache_server == 'memcache':
        require.service.restarted('memcached')


def setup_java():
    sudo('add-apt-repository -y ppa:webupd8team/java')
    sudo('apt-get update')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections')
    sudo('apt-get -q -y install oracle-java8-installer')
    print(green('Java installed.'))


@task
def setup_gunicorn():
    with source_virtualenv():
        run(env.pip + " install gunicorn")

@task
def setup_uwsgi():
    with source_virtualenv():
        run(env.pip + " install uwsgi")


@task
def setup_celery():
    with source_virtualenv():
        run(env.pip + " install django-celery celery redis")


@task
def fixdpkg():
    sudo('dpkg --configure -a')


def setup_solr():
    with source_virtualenv():
        run(env.pip + " install pysolr")

    with settings(abort_exception=FabricException):
        try:
            sudo('mkdir %s' % env.downloads, user=env.user)
        except FabricException:
            pass

    with cd(env.projects_dir):
        run('wget http://archive.apache.org/dist/lucene/solr/4.7.2/solr-4.7.2.tgz')
        run('tar xzf solr-4.7.2.tgz')
        with cd('solr-4.7.2/example/solr/collection1'):
            with settings(abort_exception=FabricException):
                try:
                    run('mv conf conf.original')
                    run('ln -s %s/sites/sandbox/deploy/solr conf' % env.oscar_dir)
                except FabricException:
                    pass

        # start solr
        with cd('solr-4.7.2/example'):
            setup_java()

    setup_solr_supervisor()
    print(green('Solr installed.'))


@task
def test_solr():
    with cd(Path(env.projects_dir, 'solr-4.7.2/example')):
        run('java -jar start.jar')


@task
def rebuild_index():
    with cd(env.docroot):
        with source_virtualenv():
            run(env.python + " /%s/manage.py rebuild_index --noinput" % env.project_dir)

    print(green('Indexes rebuilt.'))


def update():
    with cd(env.project_dir):
        run('git pull origin master')
        with source_virtualenv():
            run('find . -name "*.pyc" -exec rm -rf {} \;')
            with settings(abort_exception=FabricException):
                try:
                    sudo('service apache2 stop')
                except FabricException:
                    pass
            sudo('service nginx restart')
            sudo('service supervisor restart')


def cleanup():
    sudo('apt-get autoremove')
    sudo('apt-get -y autoclean && apt-get -y clean')


def create_user(username):
    sudo('useradd %s' % username)
    sudo('echo %s | passwd %s' % (username, username))
    sudo('chage -d 0 %s' % username)


def setup_backup():
    """
    Backup databases and configs
    """
    sudo("pip install fabric unipath")
    backup_dir = env.local_proj.parent.child('backup', 'fabfile.py.py')
    with cd(env.project_dir):
        run('mkdir -p %s/backup' % env.project_dir)
        put(backup_dir, "%s/backup/" % env.project_dir)
        # setup crontab
        # setup_private_key()


def setup_private_key():
    run('ssh-keygen -b 2048')
    backup_dir = env.local_proj.parent.child('backup', 'config')
    put(backup_dir, env.ssh)
    sudo('chmod 0600 %s/config' % env.ssh)
    sudo('echo backup %s >> /etc/hosts' % env.backup_host)

    with cd(backup_dir):
        run('fab send_key')


def restore():
    backup_dir = '%s/backup' % env.project_dir
    with cd(backup_dir):
        run('fab restore')


def backup():
    backup_dir = '%s/backup' % env.project_dir
    with cd(backup_dir):
        run('fab backup')


@task
def destroy_mysql():
    with settings(abort_exception=FabricException):
        try:
            sudo('service mysql stop')  #or mysqld
            sudo('killall -9 mysql')
            sudo('killall -9 mysqld')
        except FabricException:
            pass
    sudo('apt-get -y remove --purge mysql-server mysql-client mysql-common')
    sudo('apt-get -y autoremove')
    sudo('apt-get -y autoclean')
    sudo('deluser mysql')
    sudo('rm -rf /var/lib/mysql')
    sudo('apt-get -y purge mysql-server-core-5.5')
    sudo('apt-get -y purge mysql-client-core-5.5')
    sudo('rm -rf /var/log/mysql')
    sudo('rm -rf /etc/mysql')


@task
def destroy_postgresql():
    with settings(abort_exception=FabricException):
        try:
            sudo('service postgresql stop')
            sudo('killall psql')
        except FabricException:
            pass
    sudo('apt-get -y  --purge remove postgresql\*')
    with settings(abort_exception=FabricException):
        try:
            sudo('rm -r /etc/postgresql/')
        except FabricException:
            pass
    with settings(abort_exception=FabricException):
        try:
            sudo('rm -r /etc/postgresql-common/')
            sudo('rm -r /var/lib/postgresql/')
        except FabricException:
            pass

    sudo('userdel -r postgres')
    sudo('groupdel postgres')


def report():
    report = []
    report.append("""
Sandbox
-------
host: %(domain)s/admin/login/?next=/admin/
username: superuser
email: superuser@example.com
password: testing
    """ % {'domain': env.site['domain']})

    report.append("\n" + 20*'=' + ' Site ' + 20*'=' )
    dbs = []
    for k,v in env.site.items():
        dbs.append(str(k) + ': '+str(v))
    report.append("\n".join(dbs))

    report.append("\n" + 20*'=' + ' Database ' + 20*'=' )
    report.append(env.db_server)
    dbs = []
    for k,v in env.db.items():
        dbs.append(str(k) + ': '+str(v))
    report.append("\n".join(dbs))

    report.append("\n" + 20*'=' + ' Cache server ' + 20*'=' )
    report.append(env.cache_server)
    dbs = []
    for k,v in env.redis.items():
        dbs.append(str(k) + ': '+str(v))
    report.append("\n".join(dbs))
    print("\n".join(report))

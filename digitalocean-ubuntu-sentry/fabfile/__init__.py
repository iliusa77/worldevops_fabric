import os
from fabric.api import *
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
from fabtools.python import virtualenv
from worldevops import *


host = 'demo.loc'

env.hosts = [host]
env.project = 'sentry'
env.http_server = 'nginx'  # apache2|nginx
env.wsgi = 'gunicorn'      # gunicorn | uwsgi
env.broker = 'redis'       # redis | rabbitmq
env.broker_str = ''        # for django settings
env.install_from = 'git'   # install from git | pip

env.db = {
    'driver': 'mysql',
    'port': 3306,
    'root': genpass(),
    'name': env.project,
    'user': env.project,
    'pass': genpass(),
    'host': 'localhost',
}
#  MySQL
# env.db['url'] = 'mysql://%(user)s:%(pass)s@%(host)s:%(port)d/%(name)s' % env.db

#  PostgreSQL
env.db['driver'] = 'pgsql'  # you can choose from mysql|postgresql|sqlite
env.db['port'] = 5432
env.db['url'] = 'postgres://%(user)s:%(pass)s@%(host)s:%(port)d/%(name)s' % env.db


env.db_str = ''  # db setting string for django settings.conf file
env.cache_server = 'redis'  # memcache redis localmem db fs
env.cache_str = None
env.ssl_str = None  # ssl support in settings.py
env.installed_apps = []

env.home = Path('/', 'home', env.user)
env.ssh = '/home/%s/.ssh' % env.user

env.local_root = Path(__file__).ancestor(2)
env.projects_dir = Path('/', 'home', env.user, 'projects')
env.project_dir = Path(env.projects_dir, env.project)
env.docroot = Path(env.project_dir, env.project)
env.downloads = Path('/', 'home', env.user, 'downloaded')

env.site = {
    'domain': host,  # without www.
    'docroot': env.docroot,
    'ssl': False,
    'port': 80,
    'login': 'admin',
    'admin': 'admin@' + host,
    'admin_pwd': genpass()
}

env.redis = {
    'port': 6380,
    'pass': genpass(),
    'host': '127.0.0.1',
    'clients': [
        '127.0.0.1',
        'localhost',
        env.site['domain']
    ]
}

env.rabbitmq = {
    'login': 'sentry',
    'port': 5672,
    'pass': 'SeNtRy'
}

env.memcache = {
    'port': 11211,
    'pass': genpass(),
    'clients': [
        '127.0.0.1',
        'localhost',
        env.site['domain']
    ]
}

env.venv = Path(env.home, 'envsentry')
env.packages = Path(env.venv, 'lib', 'python2.7', 'site-packages')
env.gunicorn = os.path.join(env.venv, Path('bin', 'gunicorn'))
env.uwsgi = os.path.join(env.venv, Path('bin', 'uwsgi'))
env.python = os.path.join(env.venv, Path('bin', 'python'))

env.sentry = {
    # 'conf': '/home/{}/.sentry'.format(env.user),
    'conf': '/etc/sentry',
    'bin': os.path.join(env.venv, Path('bin', 'sentry')),
    'port': 9000,
    'host': 'localhost'  # host or ip
}

env.project_dir = os.path.join(env.venv, Path('bin'))


def setup():
    fabtools.require.system.locale('en_US.UTF-8')
    fabtools.deb.update_index()

    fabtools.require.deb.packages([
        'imagemagick', 'libxml2-dev', 'libxml2',
        'libxslt1.1', 'libevent-2.0-5', 'libsasl2-2',
        'libldap-2.4-2', 'python-dev', 'libjpeg-dev',
        'libpcre3', 'libpcre3-dev', 'nginx', 'supervisor',
        'python-pip', 'python-virtualenv', 'gunicorn', 'fabric',
        'python-unipath', 'git', 'ufw', 'libxslt1-dev',
        'zlib1g-dev', 'libsasl2-dev', 'libldap2-dev', 'libssl-dev',
        'python-pil', 'python-nose', 'libgeos-dev', 'python-lxml',
        'libffi6', 'libffi-dev', 'python-dev', 'htop', 'vim',
        'libz-dev','libpq-dev', 'libyaml-dev', 'curl'
    ])

    # run('rm -rf {}'.format(env.projects_dir))
    # run('mkdir {}'.format(env.projects_dir))
    fabtools.require.python.virtualenv(env.venv)
    setup_broker()
    setup_db()
    setup_cache()
    setup_config()

    # sudo('rm -rf /home/{}/projects/sentryenv'.format(env.user))

    with virtualenv(env.venv):
        fabtools.require.python.setuptools()
        run('easy_install -UZ sentry[postgres]')

        if env.install_from == 'git':
            # its release 8.4.0
            #run('pip install -e git+https://github.com/getsentry/sentry.git@bb1a339#egg=sentry-dev')
            fabtools.require.deb.packages(['nodejs-legacy','npm'])
            # sudo('curl --silent --location https://deb.nodesource.com/setup_5.x | bash -')
            # sudo('apt-get install nodejs')
            # run('pip install -e git+https://github.com/getsentry/sentry.git@master#egg=sentry-dev')
        else:
            fabtools.require.python.package('sentry')

        fabtools.require.python.packages(['celery[redis]'])
        # run('pip install sentry --upgrade')
        # run('pip install - U celery[redis]')
        # run('pip install raven --upgrade')

        setup_supervisor()
        # Require an email server
        fabtools.require.postfix.server(env.host_string)

    if env.http_server == 'apache2':
        proxy = """
ProxyPass / http://{host}:{port}/
ProxyPassReverse / http://{host}:{port}/
ProxyPreserveHost On
RequestHeader set X-Forwarded-Proto "https" env=HTTPS
        """.format(**env.sentry)
        fabtools.require.apache.site(config_name='sentry', template_contents=proxy, enabled=True, check_config=True)

    if env.http_server == 'nginx':
        # Require an nginx server proxying to our app
        fabtools.require.nginx.proxied_site(
            env.host,
            docroot=env.docroot,
            proxy_url='http://{host}:{port}'.format(**env.sentry)
        )

    fabtools.service.stop('supervisor')
    fabtools.cron.add_task('cleanup', '0 3 * * *', 'sentry', 'sentry cleanup --days=30')
    if env.broker == 'rabbitmq':
        fabtools.service.start('rabbitmq-server')

    fabtools.require.service.started('postgresql')
    with settings(abort_exception=FabricException):
        try:
            setup_app()
        except FabricException:
            pass

    report()
    print(green('Done'))
    with settings(abort_exception=FabricException):
        try:
            fabtools.require.service.started('supervisor')
        except FabricException:
            pass
    fabtools.require.service.started('nginx')


def setup_redis():
    fabtools.require.deb.package('redis-server')
    with virtualenv(env.venv):
        fabtools.require.python.packages(['redis', 'django-redis'])
    # When using unix domain sockets
    # Note: ``LOCATION`` needs to be the same as the ``unixsocket`` setting
    # in your redis.conf
    # append to settings.conf
    # from fabtools.shorewall import Ping, SSH, hosts, rule
    #
    # # The computers that will need to talk to the Redis server
    # # Setup a basic firewall
    # fabtools.require.shorewall.firewall(
    #     rules=[
    #         Ping(),
    #         SSH(),
    #         rule(port=env.redis['port'], source=hosts(env.redis['clients'])),
    #     ]
    # )
    # Make the Redis instance listen on all interfaces
    fabtools.require.redis.instance('sentry', bind='0.0.0.0', port=env.redis['port'], requirepass=env.redis['pass'])
    fabtools.require.service.restarted('redis-server')
    # 'LOCATION': 'unix:/var/run/redis/redis.sock:1',
    env.cache_str = ''' {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': '%(host)s:%(port)s',
            'OPTIONS': {
                'PASSWORD': '%(pass)s',
                'PICKLE_VERSION': -1,  # default
                'PARSER_CLASS': 'redis.connection.HiredisParser',
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
        },
    }
    ''' % env.redis

    # env.installed_apps.append('"django-redis"')

    sudo("update-rc.d redis-server defaults")
    print(green('Redis installed.'))


def setup_rabbitmq():
    fabtools.require.deb.package('rabbitmq-server')
    env.broker_str = 'amqp://{login}:{pass}@localhost:{port}/sentry'.format(**env.rabbitmq)


def setup_broker():
    if env.broker == 'rabbitmq':
        setup_rabbitmq()

    if env.broker == 'redis':
        fabtools.require.deb.package('redis-server')
        with virtualenv(env.venv):
            fabtools.require.python.package('redis')
        env.broker_str = 'redis://:{pass}@{host}:{port}/0'.format(**env.redis)
        # env.broker_str = 'redis+socket:///path/to/redis.sock'


def setup_supervisor():

    sentry_conf = Path(env.sentry['conf'], 'settings.py')
    fabtools.require.supervisor.process(
        'sentry-web',
        command=env.sentry['bin'] + ' --config=' + sentry_conf + ' start',
        directory=env.project_dir,
        user=env.user,
        stdout_logfile='syslog',
        stderr_logfile='syslog',
        environment='SENTRY_CONF="/etc/sentry"'
    )

    fabtools.require.supervisor.process(
        'sentry-worker',
        # command=env.sentry + ' celery worker -B',
        command=env.sentry['bin'] + ' --config=' + sentry_conf + ' celery worker -l WARNING',
        directory=env.project_dir,
        user=env.user,
        autostart=True,
        autorestart=True,
        redirect_stderr=True,
        stdout_logfile='syslog',
        stderr_logfile='syslog',
        environment='SENTRY_CONF="/etc/sentry"',
        killasgroup=True
    )

    #  see https://docs.getsentry.com/on-premise/server/queue/
    fabtools.require.supervisor.process(
        'sentry-cron',
        command=env.sentry['bin'] + ' --config=' + sentry_conf + ' celery beat',
        directory=env.project_dir,
        user=env.user,
        autostart=True,
        autorestart=True,
        redirect_stderr=True,
        stdout_logfile='syslog',
        stderr_logfile='syslog',
        environment='SENTRY_CONF="/etc/sentry"',
        killasgroup=True
    )


def setup_cache():
    if env.cache_server == 'redis':
        setup_redis()
    elif env.cache_server == 'db':
        setup_dbcache()
    elif env.cache_server == 'fs':
        setup_fscache()
    elif env.cache_server == 'localmem':
        setup_locmemcache()
    elif env.cache_server == 'memcache':
        setup_memcache()
    else:
        setup_dummycache()


def setup_dbcache():
    env.cache_str = """ {
            'default': {
                'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
                'LOCATION': 'my_cache_table',
            }
        }
    """
    with cd(env.project_dir):
        with virtualenv(env.venv):
            run('python manage.py createcachetable')


def setup_fscache():
    env.cache_str = """ {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/var/tmp/django_cache',
        }
    }
    """


def setup_locmemcache():
    env.cache_str = """ {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }
    """


def setup_dummycache():
    env.cache_str = """ {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }
    """


def setup_memcache():
    fabtools.require.deb.packages(['memcached', 'libmemcached-dev', 'python-pylibmc'])

    with virtualenv(env.venv):
        fabtools.require.python.packages(['django-memcached', 'pylibmc', 'django-pylibmc'])

    # env.cache_str = """{
    #    'default': {
    #        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
    #        'LOCATION': '127.0.0.1:%s' ,
    #    }
    # }""" % env.memcache['port']

    # pylibmc alternative
    env.cache_str = """{
    'default': {
        'BACKEND': 'django_pylibmc.memcached.PyLibMCCache',
        'LOCATION': 'localhost:11211',
        'TIMEOUT': 500,
        'BINARY': True,
        'OPTIONS': {  # Maps to pylibmc "behaviors"
            'tcp_nodelay': True,
            'ketama': True
        }
    }}"""

    env.installed_apps.append('"django-pylibmc"')

    print(green('Memcache installed.'))


def setup_app():
    with virtualenv(env.venv):
        sentry_conf = Path(env.sentry['conf'], 'settings.py')
        run('pip install sentry --upgrade')
        # run('sentry --config=%s repair' % sentry_conf)
        # run('sentry init --config={}'.format(sentry_conf))
        #run('pip install django-jsonfield==0.9.13') # fix https://github.com/getsentry/sentry/issues/1648
        run('sentry --config={} django syncdb'.format(sentry_conf))

        run('sentry --config={} upgrade'.format(sentry_conf))
        #run('sentry createuser --email={admin} --password={admin_pwd} --superuser'.format(**env.site))
        # run('sentry --config={} upgrade --noinput'.format(sentry_conf))
        # run('sentry --config=/home/%s/.sentry/settings.conf start' % env.user)


def create_admin():
    with virtualenv(env.venv):
        run(""" echo "from django.contrib.auth.models import User;
User.objects.create_superuser('%(login)s', '%(admin)s', '%(admin_pwd)s')" | """ % env.python + " manage.py shell")


def setup_config():
    import random
    secret_key = ''.join(
        [random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for _ in range(50)])

    context = {
        'PROJECT': 1, #  project id
        'SECRET_KEY': secret_key,
        'DOMAIN': env.site['domain'],
        'DATABASES': env.db_str,
        'ADMIN_EMAIL': env.site['admin'],
        'CACHES': env.cache_str,
        'REDIS_HOST': env.redis['host'],
        'REDIS_PORT': env.redis['port'],
        'REDIS_PASSWORD': env.redis['pass'],
        'BROKER_URL': env.broker_str,
        'DOCROOT': env.docroot,
        'PORT': env.sentry['port'],
        'HOST': env.sentry['host']
    }

    if len(env.installed_apps) == 1:
        context['INSTALLED_APPS'] = 'INSTALLED_APPS +=(' + ','.join(env.installed_apps) + ', )'
    elif len(env.installed_apps) > 0:
        context['INSTALLED_APPS'] = 'INSTALLED_APPS +=(' + ','.join(env.installed_apps) + ')'
    else:
        context['INSTALLED_APPS'] = ''

    if env.site['ssl'] == True:
        env.ssl_str = """
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True"""

    sudo('rm -rf {}'.format(env.sentry['conf']))
    sudo('mkdir {}'.format(env.sentry['conf']), env.user)

    target = Path(env.sentry['conf'], 'settings.py')
    tpldir = str(Path(env.local_root, 'templates'))

    upload_template(
        filename="settings.conf",
        destination=target,
        context=context,
        use_jinja=True,
        template_dir=tpldir,
        use_sudo=True
    )


def setup_db():
    if env.db['driver'] == 'pgsql':
        fabtools.require.postgres.server()
        fabtools.require.deb.packages(['postgresql-server-dev-9.3', 'postgresql-client', 'python-psycopg2'])
        with virtualenv(env.venv):
            fabtools.require.python.package('psycopg2')
            # run(env.pip + ' install psycopg2')

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

        fabtools.require.postgres.user(env.db['user'], env.db['pass'])
        fabtools.require.postgres.database(env.db['name'], owner=env.db['user'])
        print(green('PostgreSQL installed and running.'))

    if env.db['driver'] == 'mysql':
        debconf_defaults = [
            "mysql-server-5.5 mysql-server/root_password password %s" % env.db['root'],
            "mysql-server-5.5 mysql-server/root_password_again password %s" % env.db['root'],
            ]
        sudo("echo '%s' | debconf-set-selections" % "\n".join(debconf_defaults))

        with settings(abort_exception=FabricException):
            try:
                sudo('apt-get -y install mysql-server')
            except FabricException:
                sudo('apt-get -f -y install')

        fabtools.require.deb.packages(['python-mysqldb', 'libmysqlclient-dev'])
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
        with settings(mysql_user='root', mysql_password=env.db['root']):
            fabtools.require.mysql.user(env.db['user'], env.db['pass'])
        with settings(mysql_user='root', mysql_password=env.db['root']):
            fabtools.require.mysql.database(env.db['name'], owner=env.db['user'])

        with virtualenv(env.venv):
            fabtools.require.python.package('mysql-python')

        fabtools.require.service.started('mysql')
        print(green('MySQL installed and running.'))


def worldevops():
    env.hosts = [host]
    env.user = 'worldevops'


def client():
    env.hosts = [host]
    # env.user                         |  these come as args from install.py
    # env.password = '' # password     |

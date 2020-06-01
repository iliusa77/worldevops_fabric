from fabric.api import *
from fabric.contrib.files import upload_template
from fabtools import require
import fabtools
from unipath import Path
from fabric.colors import green
from worldevops import *


env.project = 'mattermost'
commonname = 'mymattermost.com'
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)

env.db = {
    'host': 'localhost',
    'ip': '192.168.33.10',
    'name': env.project,
    'user': env.user,
    'pass': genpass(),
    'root': genpass(),
    'type': 'postgresql',
    'port': 5432,
    'driver': 'org.postgresql.Driver',
    'db': 'postgres'
}

env.site = {
    'domain': commonname,  # without www.
    'docroot': env.project_dir,
    'ssl': True,
    'certfile': '/etc/nginx/ssl/{}'.format(env.project),
    'keyfile': '/etc/nginx/ssl/{}'.format(env.project),
    'user': env.user,
}

#Change to client company details
env.reqdata = {
    'country': 'GB',
    'state': 'Nottingham',
    'locality': 'Nottinghamshire',
    'organization': '{}'.format(commonname),
    'commonname': commonname,
    'domain': env.project
}


def setup_postgres():
    with settings(abort_exception=FabricException):
        try:
            fabtools.require.postgres.server()
        except FabricException:
            sudo('apt-get -f -y install')
    fabtools.require.deb.packages(['postgresql-server-dev-9.3', 'postgresql-client', 'postgresql-contrib'])

    env.db_str = '''
parameters:
    database_driver:   %(driver)s
    database_host:     %(host)s
    database_port:     %(port)s
    database_name:     %(name)s
    database_user:     %(user)s
    database_password: %(pass)s
    locale:            en
    ''' % {
        'driver': env.db['driver'],
        'name': env.db['name'],
        'user': env.db['user'],
        'pass': env.db['pass'],
        'host': env.db['host'] or 'localhost',
        'port': env.db['port'] or 5432
    }

    fabtools.require.postgres.user(env.db['user'], env.db['pass'])
    fabtools.require.postgres.database(env.db['name'], owner=env.db['user'])
    with cd('/etc/postgresql/9.3/main'):
        upload_template(
            filename=Path('./', 'config', 'postgresql.conf'),
            destination=('/etc/postgresql/9.3/main/postgresql.conf'),
            use_sudo=True
        )
    sudo('/etc/init.d/postgresql reload')
    print(green('PostgreSQL installed and running.'))

def install_mattermost():
    with cd('/home/{}'.format(env.user)):
        sudo('wget https://releases.mattermost.com/3.2.0/mattermost-team-3.2.0-linux-amd64.tar.gz')
        sudo('tar -xvzf mattermost-team-3.2.0-linux-amd64.tar.gz')
        sudo('mkdir -p mattermost/data')
        sudo('chown -R {} mattermost/'.format(env.user))

def setup_mattermost():
    with cd('/home/{}/mattermost/config'.format(env.user)):
        upload_template(
            filename=Path('./', 'config', 'config.json'),
            destination=('/home/{}/mattermost/config/config.json'.format(env.user)),
            context=env.db, use_sudo=True
        )
    with cd('/etc/init/'):
        upload_template(
            filename=Path('./', 'config', 'mattermost.conf'),
            destination=('/etc/init/mattermost.conf'),
            context=env.db, use_sudo=True
        )
    sudo('start mattermost')

def genssl():
    sudo('mkdir -p /etc/nginx/ssl')
    with cd('/etc/nginx/ssl'):
        sudo('openssl genrsa -des3 -passout pass:x -out {}.pass.key 2048'.format(env.project))
        sudo('openssl rsa -passin pass:x -in {0}.pass.key -out {0}.key'.format(env.project))
        sudo('rm {}.pass.key'.format(env.project))
        sudo('openssl req -new -key %(domain)s.key -out %(domain)s.csr \
        -subj "/C=%(country)s/ST=%(state)s/L=%(locality)s/O=%(organization)s/CN=%(commonname)s"' % env.reqdata)
        sudo('openssl x509 -req -days 365 -in {0}.csr -signkey {0}.key -out {0}.crt'.format(env.project))

def setup_nginx():
    fabtools.require.nginx.server()
    if env.site['ssl'] == True:
        upload_template(
            filename=Path('./', 'nginx', 'ssl-site.conf'),
            destination='/etc/nginx/sites-available/ssl-{}.conf'.format(env.project),
            context=env.site, use_sudo=True
        )
        sudo("ln -s /etc/nginx/sites-available/ssl-{0}.conf /etc/nginx/sites-enabled/ssl-{0}.conf".format(env.project))
    else:
        upload_template(
            filename=Path('./', 'nginx', 'site.conf'),
            destination='/etc/nginx/sites-available/{}.conf'.format(env.project),
            context=env.site, use_sudo=True
        )
        sudo("ln -s /etc/nginx/sites-available/{0}.conf /etc/nginx/sites-enabled/{0}.conf".format(env.project))
    fabtools.service.reload('nginx')

def credentials():
    print(green('You can access your site by URL https://%s/' % env.site['domain']))
    print(green('---------------------------------------------------------------'))
    print('\n')
    print(green('POSTGRESQL database'))
    print(green('------------------------------------'))
    print('Host: %s' % env.db['host'])
    print('Database name: %s' % env.db['name'])
    print('Database user: %s' % env.db['user'])
    print('Database user password: %s' % env.db['pass'])
    print('Database root password: %s' % env.db['root'])
    print('\n')

def setup():
    sudo('apt-get update && apt-get -y upgrade')
    setup_postgres()
    install_mattermost()
    setup_mattermost()
    genssl()
    setup_nginx()
    credentials()

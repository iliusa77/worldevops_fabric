import os
from fabric.api import *
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.api import settings
from fabric.colors import green
import fabtools

def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))


class FabricException(Exception):
    pass


# the servers where the commands are executed
env.hosts = ['192.168.35.10']
env.project = 'brokertool'
env.proroot = Path('/', 'var', 'www')
env.docroot = Path(env.proroot, 'public')
env.localwd = Path(__file__).ancestor(1)

# # the user to use for the remote commands
env.user = 'vagrant'
env.password = 'vagrant'
env.user_pwd = 'vagrant'

env.site = {
    'domain': '192.168.35.10',  # without www.
    'docroot': env.docroot,
    'ssl': False,
    'port': 80,
    'admin': 'admin@example.com'
}

env.db = {
    'root': genpass(),
    'name': env.project,
    'user': env.project,
    'pass': genpass(),
    'host': 'localhost',
}

#  PostgreSQL
# env.db_server = 'pgsql'  # you can choose from mysql|postgresql|sqlite
# env.db['port'] = 5432
# env.db['url'] = 'postgres://%(user)s:%(pass)s@%(host)s:%(port)d/%(name)s' % env.db

#  MySQL
env.db_server = 'mysql'  # you can choose from mysql|pgsql|sqlite
env.db['port'] = 3306
env.db['url'] = 'mysql://%(user)s:%(pass)s@%(host)s:%(port)d/%(name)s' % env.db


def setup():
    setup_mysql()
    setup_php()
    setup_nginx()
    setup_composer()
    source = Path(env.localwd, 'config', 'autoload', 'local.php.dist')
    target = Path(env.proroot, 'config', 'autoload', 'local.php')
    run('cp {0} {1}'.format(source, target))


def update():
    with lcd(env.localwd):
        local('php composer.phar update')

    setup_nginx()
    # setup_apache()
    # setup_composer()

    with cd(env.docroot):
        run('php index.php orm:schema-tool:update --force')
        run('php index.php migration apply')


def setup_mysql():
    fabtools.require.deb.packages(['mysql-client', 'libmysqlclient-dev', 'mysql-server-5.6', 'php5-mysql'])
    fabtools.require.mysql.server(password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.user(env.db['user'], env.db['pass'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.database(env.db['name'], owner=env.db['user'])
    fabtools.require.service.started('mysql')

    print(green('MySQL installed and running.'))


def setup_php():
    fabtools.require.deb.packages([
        'php5-fpm',
        'php5-cli',
        'libxml2-dev',
        'php5-json',
        'php5-mysql',
        'php5-gd',
        'php5-curl',
        'php5-intl',
    ])


def setup_nginx():
    fabtools.require.nginx.server()
    source = Path(env.localwd, 'etc', 'nginx', 'site.conf')
    target = Path('/', 'etc', 'nginx', 'sites-available', '%s.conf' % env.project)
    upload_template(source, target, use_sudo=True,
        context={'domain': env.site['domain'],
                 'project': env.project,
                 'docroot': env.docroot
        }
    )

    fabtools.nginx.enable(env.project + '.conf')
    fabtools.require.service.started('nginx')
    print(green('Done'))


def setup_apache():
    fabtools.require.apache.server()
    source = Path(env.localwd, 'etc', 'apache2', 'site.conf')
    target = Path('/', 'etc', 'apache2', 'sites-available', '%s.conf' % env.project)
    upload_template(source, target, use_sudo=True,
                    context={'domain': env.site['domain'],
                             'project': env.project,
                             'docroot': env.docroot
                             }
                    )

    fabtools.apache.enable(env.project + '.conf')
    fabtools.require.service.started('apache')
    print(green('Done'))


def setup_composer():
    """@setup git, composer"""
    sudo('curl -sS https://getcomposer.org/installer | php')
    sudo('mv composer.phar /usr/local/bin/composer')
    print(green('Composer installed'))


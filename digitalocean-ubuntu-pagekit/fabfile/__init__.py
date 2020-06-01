"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10,project={project_name},http_server={apache or nginx},dbtype={mysql or sqlite} setup

"""
from fabric.api import *
from fabtools import require
import requests
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
import hashlib
import sys
root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *

env.project = 'pagekit'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))


env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': genpass(),
    'port': 3306,
    'root': genpass(),
    'prefix': 'pk_'
}


env.app = {
    'title': 'PageKit',
    'user': 'admin',
    'password': genpass(),
    'email': 'youremail@email.com',
    'locale': 'en_GB'
}


def prepare_nginx_server():
    sudo('apt-get update && apt-get -y dist-upgrade')
    fabtools.require.nginx.server()
    common_setup()
    setup_mail_server()
    fabtools.require.deb.packages([
        'php5-fpm','zip','php5-json','php-apc'
    ])
    upload_php_config()
    fabtools.require.git.command()


def prepare_apache_server():
    sudo('apt-get update && apt-get -y dist-upgrade')
    fabtools.require.apache.server()
    fabtools.require.apache.module_enabled('rewrite')
    common_setup()
    setup_mail_server()
    fabtools.require.deb.packages([
        'php5','zip','php5-json','php-apc'
    ])
    fabtools.require.git.command()



def upload_php_config():
    put(Path(env.local, 'php', 'php-fpm.ini'), '/etc/php5/fpm/php.ini', use_sudo=True)
    fabtools.service.stop('php5-fpm')
    fabtools.service.start('php5-fpm')


def setup_domain(stype):
    if stype == 'nginx':
        fabtools.require.nginx.site(env.project,
                           template_source=Path(env.local,'nginx','production.conf'),
                           domain=env.domain,
                           docroot=env.project_dir
                           )
        fabtools.require.service.start('nginx')
    if stype == 'apache':
        fabtools.require.apache.site(env.project,
                            template_source=Path(env.local,'apache','site.conf'),
                            domain=env.domain,
                            docroot=env.project_dir,
                            port = 80
                            )
        fabtools.require.service.start('apache2')


def setup_db():
    if env.dbtype == 'mysql':
        install_mysql()
        fabtools.require.deb.packages(['php5-mysql'])
    if env.dbtype == 'sqlite':
        fabtools.require.deb.packages(['sqlite3', 'libsqlite3-dev', 'php5-sqlite'])


def chmod():
    with cd(env.project_dir):
        run('chmod +x pagekit')
        run('chmod -R 777 tmp')
    with cd(env.home):
        sudo('chmod 777 %s' %env.project)


def setup_project():
    if fabtools.files.is_dir(env.project_dir):
        sudo('rm -rf ' + env.project_dir)
    run('mkdir -p ' + env.project_dir)
    with cd(env.project_dir):
        run('wget -O source.zip https://pagekit.com/api/download/latest')
        run('unzip source.zip -d .')
        run('rm -f source.zip')
        chmod()
        run('./pagekit setup --username=%s --password=%s --title=%s --mail=%s --db-driver=%s --db-prefix=%s --db-host=%s --db-name=%s --db-user=%s --db-pass=%s --locale=%s' \
            %(env.app['user'], env.app['password'], env.app['title'], env.app['email'], env.dbtype, env.db['prefix'], env.db['host'], env.db['name'], env.db['user'], env.db['pass'], env.app['locale']))


def setup_with_apache():
    prepare_apache_server()
    setup_db()
    setup_project()
    setup_domain('apache')
    print(green('Done'))
    report()


def setup_with_nginx():
    prepare_nginx_server()
    setup_db()
    setup_project()
    setup_domain('nginx')
    print(green('Done'))
    report()


def setup():
    if env.http_server == 'nginx':
        setup_with_nginx()
    else:
        setup_with_apache()

def report():
    print(green('You can access your site by URL http://%s/' % env.domain))
    print(green('------------------------------------'))
    if env.dbtype == 'mysql':
        print('\n')
        print(green('MYSQL database'))
        print(green('------------------------------------'))
        print('Host: %s' % env.db['host'])
        print('Database name: %s' % env.db['name'])
        print('Database user: %s' % env.db['user'])
        print('Database user password: %s' % env.db['pass'])
        print('Root database access: root with password %s' %env.db['root'])
        print('\n')
    print(green('Pagekit user'))
    print(green('------------------------------------'))
    print('Login: %s' % env.app['user'])
    print('Password: %s' % env.app['password'])
    print('Email: %s' % env.app['email'])
"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10,project={project_name},http_server={apache or nginx} setup

"""
import sys
import fabtools
import requests
from fabric.api import *
from fabtools import require
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
from fabric.colors import red

root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *


class FabricException(Exception):
    pass


env.project = 'hesk'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))

env.db = {
    'driver': 'mysql',
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': genpass(),
    'port': 3306,
    'root': genpass(),
}


def prepare_nginx_server():
    sudo('apt-get update && apt-get -y dist-upgrade')
    fabtools.require.nginx.server()
    common_setup()
    setup_mail_server()
    fabtools.require.deb.packages([
        'php5-fpm', 'zip', 'php5-mysql'
    ])
    upload_php_config()


def prepare_apache_server():
    sudo('apt-get update && apt-get -y dist-upgrade')
    fabtools.require.apache.server()
    fabtools.require.apache.module_enabled('rewrite')
    common_setup()
    setup_mail_server()
    fabtools.require.deb.packages([
        'php5', 'zip', 'php5-mysql'
    ])


def upload_php_config():
    put(Path(env.local, 'php', 'php-fpm.ini'), '/etc/php5/fpm/php.ini', use_sudo=True)
    fabtools.service.stop('php5-fpm')
    fabtools.service.start('php5-fpm')


def setup_domain(stype):
    if stype == 'nginx':
        fabtools.require.nginx.site(
            env.project,
            template_source=Path(env.local, 'nginx', 'site.conf'),
            domain=env.domain,
            docroot=env.project_dir,
            port=80
        )
        fabtools.require.service.start('nginx')
    if stype == 'apache':
        fabtools.require.apache.site(
            env.project,
            template_source=Path(env.local, 'apache', 'site.conf'),
            domain=env.domain,
            docroot=env.project_dir,
            port=80
        )
        fabtools.require.service.start('apache2')


def chmod():
    with cd(env.project_dir):
        run('chmod -R 777 attachments')
        run('chmod 777 hesk_settings.inc.php')


def setup_project():
    # if fabtools.files.is_dir(env.project_dir):
    #     sudo('rm -rf ' + env.project_dir)
    # run('mkdir -p ' + env.project_dir)
    with cd(env.project_dir):
        put(Path(env.local, 'source', 'source.zip'), env.project_dir, use_sudo=True)
        run('unzip source.zip -d .')
        run('rm -f source.zip')
    chmod()


def setup_with_apache():
    prepare_apache_server()
    install_mysql()
    setup_project()
    setup_domain('apache')
    print(green('Done'))
    report()


def setup_with_nginx():
    prepare_nginx_server()
    install_mysql()
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
    print(green(
        'You can access your site by URL http://%s/install/ and continue installation in browser using database credentials below' % env.domain))
    print(green('------------------------------------'))
    print(green('MYSQL database'))
    print(green('------------------------------------'))
    print('Host: %s' % env.db['host'])
    print('Database name: %s' % env.db['name'])
    print('Database user: %s' % env.db['user'])
    print('Database port: %s' % env.db['port'])
    print('Database user password: %s' % env.db['pass'])
    print('Root database access: root with password %s' % env.db['root'])
    print('\n')

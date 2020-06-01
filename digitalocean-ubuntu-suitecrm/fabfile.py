"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10,project={project_name},http_server={apache or nginx} setup

"""
from fabric.api import *
from fabtools import require
import requests
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
import sys

root = Path(__file__).ancestor(2)
sys.path.append(root)
from worldevops import *

env.project = 'suitecrm'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)


class FabricException(Exception):
    pass


env.site = {
    'domain': env.domain,
    'login': 'admin',
    'password': genpass(),
}

env.db = {
    'driver': 'mysql',
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': genpass(),
    'port': 3306,
    'root': genpass()
}

env.ssh = '/home/%s/.ssh' % env.user

repo = 'https://github.com/salesagility/SuiteCRM.git'
path = env.project_dir


def prepare_nginx_server():
    sudo('apt-get update && apt-get -y dist-upgrade')
    fabtools.require.nginx.server()
    install_mysql()
    setup_mail_server()
    fabtools.require.deb.packages([
        'php5-fpm'
    ])
    setup_mods()
    upload_php_config('php-fpm')
    fabtools.require.git.command()


def prepare_apache_server():
    sudo('apt-get update && apt-get -y dist-upgrade')
    fabtools.require.apache.server()
    fabtools.require.apache.module_enabled('rewrite')
    install_mysql()
    setup_mail_server()
    fabtools.require.deb.packages([
        'php5'
    ])
    setup_mods()
    upload_php_config('php')
    fabtools.require.git.command()


def setup_mods():
    fabtools.require.deb.packages([
        'php5-cli',
        'php5-mysql',
        'php5-curl',
        'php5-imap',
        'php5-gd',
    ])
    sudo('php5enmod imap')


def upload_php_config(stype):
    if stype == 'php':
        fabtools.require.deb.packages([
            'libapache2-mod-php5',
        ])
        source = Path('./', 'php', 'php.ini')
        target = '/etc/php5/apache2/php.ini'
        put(source, target, use_sudo=True)
        fabtools.service.reload('apache2')
    if stype == 'php-fpm':
        put('./php/php-fpm.ini', '/etc/php5/fpm/php.ini', use_sudo=True)
        fabtools.service.stop('php5-fpm')
        fabtools.service.start('php5-fpm')


def upload_config():
    upload_template(
        './config/config_si.php',
        Path(path),
        use_sudo=True,
        context={'db_host': env.db['host'], 'db_port': env.db['port'], 'db_name': env.db['name'],
                 'db_user': env.db['user'], 'db_password': env.db['pass'], 'db_driver': env.db['driver'],
                 'login': env.site['login'], 'password': env.site['password'], 'domain': env.site['domain']
                 }
    )
    print(green('Config uploaded'))


def setup_domain(stype):
    if stype == 'nginx':
        fabtools.require.nginx.site(env.project,
                                    template_source='./nginx/production.conf',
                                    domain=env.site['domain'],
                                    docroot=path
                                    )
        fabtools.require.service.start('nginx')
    if stype == 'apache':
        fabtools.require.apache.site(env.project,
                                     template_source='./apache/site.conf',
                                     domain=env.site['domain'],
                                     docroot=path
                                     )
        fabtools.require.service.start('apache2')


def chmod():
    with cd(path):
        sudo('chmod -R 775 cache custom modules themes data upload config_override.php')
        sudo('chmod 777 config.php')


def chown():
    with cd(path.parent):
        sudo('chown -R %s:www-data %s' % (env.user, env.project))


def setup_project():
    if fabtools.files.is_dir(path):
        run('rm -r ' + path)
    run('mkdir -p ' + path)
    with cd(path):
        run('git clone ' + repo + ' .')
        run('git checkout tags/v7.6.5')
        run('mkdir cache')
        run('touch config.php')
        run('php -f cron.php > /dev/null 2>&1')
    chown()
    chmod()


def setup_prod_final():
    print(green('Starting silent install. Please wait...'))
    params = {'goto': 'SilentInstall', 'cli': 'true'}
    url = "http://%s/install.php" % env.site['domain']
    requests.get(url, params=params, timeout=45)
    print(green('Installation complete'))
    run('rm -rf install/')
    run('rm -f install.php')


def setup_with_apache():
    prepare_apache_server()
    setup_project()
    setup_domain('apache')
    upload_config()
    setup_prod_final()
    print(green('Done'))
    report()


def setup_with_nginx():
    prepare_nginx_server()
    setup_project()
    setup_domain('nginx')
    upload_config()
    setup_prod_final()
    print(green('Done'))
    report()


def setup():
    if env.http_server == 'nginx':
        setup_with_nginx()
    else:
        setup_with_apache()


def report():
    print(green('You can access your site by URL http://%s/' % env.site['domain']))
    print(green('------------------------------------'))
    print('\n')
    print(green('MYSQL database'))
    print(green('------------------------------------'))
    print('Host: %s' % env.db['host'])
    print('Database name: %s' % env.db['name'])
    print('Database user: %s' % env.db['user'])
    print('Database user password: %s' % env.db['pass'])
    print('\n')
    print(green('SuiteCRM user'))
    print(green('------------------------------------'))
    print('Login: %s' % env.site['login'])
    print('Password: %s' % env.site['password'])


"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10,project={project_name} setup

"""
from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green, yellow
import sys
root = Path(__file__).ancestor(2)
sys.path.append(root)
from worldevops import *


env.db = {
    'driver': 'mysql',
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': genpass(),
    'root': genpass(),
    'port': 3306
}

env.phpbbadmin = {
    'name': 'admin',
    'password': genpass(),
    'email': 'email@email.com'
}

env.project = 'phpbb'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(1))

repo = 'https://github.com/phpbb/phpbb-app.git'


def _composer_is_installed():
    with settings(hide('stderr'), warn_only=True):
        output = run('composer --version')
    return output.succeeded


def setup_composer():
    """@setup composer"""
    if not _composer_is_installed():
        sudo('curl -sS https://getcomposer.org/installer | php')
        sudo('mv composer.phar /usr/local/bin/composer')
        print(green('Composer installed'))
    else:
        print(green('Composer already installed'))


def prepare_nginx_server():
    sudo('apt-get update && apt-get -y dist-upgrade')
    fabtools.require.nginx.server()
    install_mysql()
    setup_mail_server()
    fabtools.require.deb.packages([
        'php5-fpm'
    ])
    setup_mods()
    fabtools.require.git.command()


def setup_mods():
   fabtools.require.deb.packages([
       'php5-fpm',
       'php5-cli',
       'imagemagick',
       'libxml2-dev',
       'php5-json',
       'php5-mysql',
       'php5-gd',
       'libgcrypt11-dev',
       'zlib1g-dev'
   ])


def upload_config():
    upload_template(
        './config/parameters.yml',
        Path(env.project_dir, 'config'),
        use_sudo=True,
        context={'db_host': env.db['host'], 'db_port': env.db['port'], 'db_name': env.db['name'],
                 'db_user': env.db['user'], 'db_password': env.db['pass'], 'db_driver': env.db['driver'],
                 'name': env.phpbbadmin['name'], 'password': env.phpbbadmin['password'],
                 'email': env.phpbbadmin['email']}
    )
    with cd(env.project_dir):
        sudo('touch config.php')
    print(green('Config uploaded'))


def setup_domain():
    print(env.local)
    fabtools.require.nginx.site(env.project,
                       template_source=Path(env.local,'nginx','phpbb.conf'),
                       port=80,
                       domain=env.domain,
                       root=env.project_dir
                       )
    fabtools.require.nginx.enable(env.project)


def chmod():
    with cd(env.project_dir):
        sudo('chmod 777 -R cache/')
        sudo('chmod 777 -R files/')
        sudo('chmod 777 -R store/')
        sudo('chmod 777 config.php')


def chown():
    with cd(env.project_dir):
        sudo('chown -R www-data:www-data ../%s' % env.project)


def remove():
    with cd(env.project_dir):
        sudo('rm -r install')


def setup_prod():
    sudo('mkdir -p ' + env.project_dir)
    with cd(env.project_dir):
        sudo('git clone ' + repo + ' .')
        sudo('composer install')
        upload_config()
        chmod()
        sudo('php install/phpbbcli.php install config/parameters.yml')
        chmod()
        remove()
        chown()


def setup():
    sudo("apt-get update && apt-get -y dist-upgrade")
    prepare_nginx_server()
    setup_composer()
    setup_domain()
    setup_prod()
    fabtools.require.nginx.disable('default')
    fabtools.require.service.restarted("nginx")
    report()


def report():
    print(green('You can access your site by URL http://%s/' % env.domain))
    print(green('------------------------------------'))
    print('\n')
    print(green('MYSQL database'))
    print(green('------------------------------------'))
    print('Host: %s' % env.db['host'])
    print('Database name: %s' % env.db['name'])
    print('Database user: %s' % env.db['user'])
    print('Database user password: %s' % env.db['pass'])
    print('Root database access: root with password %s' %env.db['root'])
    print('\n')
    print(green('PHPBB user'))
    print(green('------------------------------------'))
    print('Login: %s' % env.phpbbadmin['name'])
    print('Password: %s' % env.phpbbadmin['password'])
    print('Email: %s' % env.phpbbadmin['email'])
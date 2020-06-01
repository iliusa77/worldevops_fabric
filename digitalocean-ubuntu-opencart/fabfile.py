"""

fab -H {host} --user=worldevops --set=domain={domain} create_app_user:{user},passwd={passwd}
fab -H {host} --user={user} --set=domain={domain} --password={passwd} setup_with_nginx

"""
from fabric.api import *
import fabtools
from unipath import Path
from fabric.colors import green
from worldevops import *

class FabricException(Exception):
    pass


env.project = 'opencart'
local_root = Path(__file__).ancestor(1)

env.site = {
    'domain': env.domain
}

env.http_server = 'nginx'

env.db = {
    'driver': 'mysqli',
    'host': 'localhost',
    'name': env.project,
    'login': env.project,
    'pass': genpass(),
    'root': genpass(),
    'port': 3306,
}

env.opencartuser = {
    'login': 'admin',
    'password': genpass(),
    'email': 'admin@' + env.domain,
}

home = Path('/', 'home', env.user)
env.ssh = Path(home, '.ssh')
repo = 'https://github.com/opencart/opencart.git'
path = Path('/', 'var', 'www', env.project)


def prepare_nginx_server():
    env.http_server = 'nginx'
    sudo('apt-get update && apt-get -y dist-upgrade')
    fabtools.require.nginx.server()
    setup_db()
    setup_php()
    setup_php_fpm()
    setup_composer()
    fabtools.require.git.command()


def prepare_apache_server():
    env.http_server = 'apache2'
    sudo('apt-get update && apt-get -y dist-upgrade')
    fabtools.require.apache.server()
    fabtools.require.apache.module_enabled('rewrite')
    setup_db()
    setup_php()
    fabtools.service.restart('apache2')
    setup_composer()
    fabtools.require.git.command()


def setup_db():
    with settings(abort_exception=FabricException):
        try:
            fabtools.require.mysql.server(password=env.db['root'])
        except FabricException:
            sudo('apt-get -f -y install')

    fabtools.require.deb.packages(['libmysqlclient-dev'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.user(env.db['login'], env.db['pass'])
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.database(env.db['name'], owner=env.db['login'])


def setup_php_fpm():
    fabtools.require.deb.packages([
        'php5-fpm',
    ])
    put('./php/php-fpm.ini', '/etc/php5/fpm/php.ini', use_sudo=True)
    fabtools.service.stop('php5-fpm')
    fabtools.service.start('php5-fpm')


def setup_composer():
    """@setup composer"""
    sudo('curl -sS https://getcomposer.org/installer | php')
    sudo('mv composer.phar /usr/local/bin/composer')
    print(green('Composer installed'))


def setup_php():
    fabtools.require.deb.packages([
        'php5',
        'php5-cli',
        'php5-curl',
        'php5-gd',
        'php5-mcrypt',
        'php5-mysql',
    ])
    sudo('php5enmod mcrypt')


def setup_http(type):
    if type is 'nginx':
        fabtools.require.nginx.site(
            env.project,
            template_source='./nginx/production.conf',
            domain=env.site['domain'],
            project=env.project,
            docroot=path
        )
        fabtools.service.restart('nginx')
    if type is 'apache':
        fabtools.require.apache.site(
            env.project,
            template_source='./apache/site.conf',
            domain=env.site['domain'],
            project=env.project,
            docroot=path
        )
        fabtools.service.restart('nginx')


def chmod():
    with cd(path):
        sudo('chmod -R 0777 system/storage/cache/')
        sudo('chmod -R 0777 system/storage/logs/')
        sudo('chmod -R 0777 system/storage/download/')
        sudo('chmod -R 0777 system/storage/upload/')
        sudo('chmod -R 0777 system/storage/modification/')
        sudo('chmod -R 0777 image/')
        sudo('chmod -R 0777 image/cache/')
        sudo('chmod -R 0777 image/catalog/')
        sudo('chmod 0777 config.php')
        sudo('chmod 0777 admin/config.php')


def chown():
    with cd(path.parent):
        sudo('chown -R %s:www-data %s' % (env.user, env.project))


def setup_prod():
    if fabtools.files.is_dir(path):
        sudo('rm -r ' + path)
    tmp = Path(path, 'tmp')
    if fabtools.files.is_dir(tmp):
        sudo('rm -rf {}'.format(tmp))
    sudo('mkdir -p {}'.format(tmp))
    ccache = Path(home, '.composer')
    if fabtools.files.is_dir(ccache):
        sudo('rm -rf ' + ccache)
    run('mkdir {}'.format(ccache))
    sudo('chown -R {0}:{1} {2}'.format(env.user, env.user, path))
    with cd(tmp):
        run('git clone {} .'.format(repo))
        run('git checkout tags/2.2.0.0')
        run('composer install')
    with cd(path):
        if fabtools.files.is_dir('/var/www/vendor'):
            sudo('rm -r /var/www/vendor')
        sudo('mv -f tmp/vendor /var/www/')
        sudo('mv -f tmp/upload/* %s' % path)
        if fabtools.files.is_file('tmp'):
            sudo('rm -R tmp')
        run('mv config-dist.php config.php')
        run('mv admin/config-dist.php admin/config.php')
    with cd(path + '/install'):
        str = "php cli_install.php install --db_hostname %s --db_username %s --db_password %s \
        --db_database %s --db_driver %s --db_port %s --username %s --password %s --email \
        %s --http_server http://%s/ --port 80" % (
            env.db['host'], env.db['login'], env.db['pass'], env.db['name'], env.db['driver'], env.db['port'],
            env.opencartuser['login'], env.opencartuser['password'], env.opencartuser['email'], env.site['domain'])
        sudo(str)
    with cd(path):
        sudo('rm -r install/')
    chown()
    chmod()


def setup_with_apache():
    prepare_apache_server()
    setup_db()
    setup_prod()
    setup_http('apache')
    setup_mail_server()
    print(green('Done'))
    report()


def setup_with_nginx():
    prepare_nginx_server()
    setup_db()
    setup_prod()
    setup_http('nginx')
    setup_mail_server()
    print(green('Done'))
    report()


def report():
    run('clear')
    print(green('You can access your site by URL http://%s/' % env.site['domain']))
    print(green('------------------------------------'))
    print('\n')
    print(green('MYSQL database'))
    print(green('------------------------------------'))
    print('Host: %s' % env.db['host'])
    print('Database name: %s' % env.db['name'])
    print('Database user: %s' % env.db['login'])
    print('Database user password: %s' % env.db['pass'])
    print('\n')
    print(green('Admin user'))
    print(green('------------------------------------'))
    print('Login: %s' % env.opencartuser['login'])
    print('Password: %s' % env.opencartuser['password'])
    print('E-mail: %s' % env.opencartuser['email'])


def setup_theme(theme):
    new_theme = Path(local_root, 'theme', theme)
    target = Path(path, 'catalog', 'view', 'theme')
    put(new_theme, target)
    sudo('apt-get update')
    fabtools.require.deb.packages(['unzip', 'tar'])
    with cd(target):
        run('unzip -x {}'.format(theme))
        run('rm -f {}'. format(theme))
        sudo('chown {user}:www-data -R *'.format(user=env.user))
        sudo('chmod g+w -R *'.format(user=env.user, theme=theme))

    chmod()

"""
command format  fab -H demo.loc --user vagrant --password vagrant --set=ip=192.168.33.10,domain=demo.loc <command>

"""
from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
from fabric.api import settings


class FabricException(Exception):
    pass


def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))


def create_app_user(user, passwd):
    print('Create application user {0} with password {1} at {2}'.format(user, passwd, env.host_string))
    fabtools.require.user(user, password=passwd, create_home=True)
    fabtools.require.users.sudoer(user, hosts='ALL', operators='ALL', passwd=False, commands='ALL')

if 'project' not in env:
    env.project = 'mautic'

# PostgreSQL	django.db.backends.postgresql_psycopg2	postgres://USER:PASSWORD@HOST:PORT/NAME
# PostGIS	    django.contrib.gis.db.backends.postgis	postgis://USER:PASSWORD@HOST:PORT/NAME
# MySQL	        django.db.backends.mysql	            mysql://USER:PASSWORD@HOST:PORT/NAME
# MySQL  (GIS)	django.contrib.gis.db.backends.mysql	mysqlgis://USER:PASSWORD@HOST:PORT/NAME
# SQLite	    django.db.backends.sqlite3	            sqlite:///PATH
# Oracle	    django.db.backends.oracle	            oracle://USER:PASSWORD@HOST:PORT/NAME
# Oracle (GIS)	django.contrib.gis.db.backends.oracle	oraclegis://USER:PASSWORD@HOST:PORT/NAME

#  MySQL
env.db = {
    'driver': 'pdo_mysql',
    'root': genpass(),
    'name': env.project,
    'user': env.project,
    'pass': genpass(),
    'host': 'localhost',
    'port': 3306
}

#  PostgreSQL
# env.db['driver'] = 'pdo_pgsql'  # you can choose from mysql|postgresql|sqlite
# env.db['port'] = 5432
# env.db['url'] = 'postgres://%(user)s:%(pass)s@%(host)s:%(port)d/%(name)s' % env.db
# Mautic doesn't support pgsql in web installation(See https://pm.worldevops-web.com/issues/13035)


env.ssh = '/home/%s/.ssh' % env.user

repo = 'https://github.com/mautic/mautic.git'
path = Path('/', 'home', env.user, env.project)


def prepare_nginx_server():
    sudo('apt-get update')
    require.nginx.server()
    setup_php_fpm()
    setup_php()
    setup_composer()
    require.git.command()
    setup_domain('nginx')


def prepare_apache_server():
    sudo('apt-get update')
    require.apache.server()
    require.apache.module_enabled('rewrite')
    require.deb.packages([
        'php5'
    ])
    setup_php()
    put('./php/php.ini', '/etc/php5/apache2/php.ini', use_sudo=True)
    fabtools.service.reload('apache2');
    setup_composer()
    require.git.command()
    setup_domain('apache')


def setup_php_fpm():
    require.deb.packages([
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
    sudo('add-apt-repository -y ppa:ondrej/php5-5.6')
    sudo('apt-get update')
    require.deb.packages([
        'php5-mysql',
        'php5-mcrypt',
        'php5-curl',
        'php5-imap',
        'libxml2-dev',
        'php5-gd',
        'php5-intl',
        'libpcre3',
        'libpcre3-dev'
    ])


def setup_db():
    if env.db['driver'] == 'pdo_pgsql':
        return setup_pgsql()

    with settings(abort_exception=FabricException):
        try:
            require.mysql.server(password=env.db['root'])
        except FabricException:
            sudo('apt-get -f -y install')

    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.user(env.db['user'], env.db['pass'])
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.database(env.db['name'], owner=env.db['user'])


def setup_pgsql():
    fabtools.require.deb.packages(['postgresql-server-dev-all', 'postgresql-client'])
    with settings(abort_exception=FabricException):
        try:
            require.postgres.server()
        except FabricException:
            sudo('apt-get -f -y install')

    require.postgres.user(env.db['user'], env.db['pass'])
    require.postgres.database(env.db['name'], env.db['user'])  # setup firewall

    require.deb.packages([
        'php5-pgsql',
    ])

    fabtools.require.service.started('postgresql')


def setup_domain(type):
    if type == 'nginx':
        require.nginx.site(
            env.project,
            template_source='./nginx/production.conf',
            domain=env.domain,
            docroot=path
        )
    if type == 'apache':
        require.apache.site(
            env.project,
            template_source='./apache/site.conf',
            domain=env.domain,
            docroot=path
        )


def chmod():
    with cd(path):
        sudo('chmod -R 777 -R app/logs')
        sudo('chmod -R 777 -R app/cache')
        sudo('chmod -R 777 -R app/config')
        sudo('chmod -R 775 media/dashboards')
        sudo('chmod -R 777 -R upgrade')


def chown():
    with cd(path.parent):
        sudo('chown -R %s:%s %s' % (env.user, env.user, env.project))
    with cd(path):
        sudo('chown -R www-data:www-data app/logs')
        sudo('chown -R www-data:www-data app/cache')
        sudo('chown -R www-data:www-data app/config')
        sudo('chown -R www-data:www-data media/dashboards')
        sudo('chown -R www-data:www-data upgrade')


def setfacl():
    require.deb.packages([
        'acl',
    ])
    fabtools.require.file('{}/setfacl.sh'.format(path), """\
#!/bin/sh
HTTPDUSER=`ps aux | grep -E '[a]pache|[h]ttpd|[_]www|[w]ww-data|[n]ginx' | grep -v root | head -1 | cut -d\  -f1`;
sudo setfacl -R -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX {0}/app/cache {0}/app/logs;
sudo setfacl -dR -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX {0}/app/cache {0}/app/logs;
""".format(path))
    run('chmod u+x {}/setfacl.sh'.format(path))
    run('/bin/sh {}/setfacl.sh'.format(path))
    run('rm {}/setfacl.sh'.format(path))


def setup_cronjobs():
    # php /path/to/mautic/app/console mautic:segments:update
    # php /path/to/mautic/app/console mautic:campaigns:rebuild
    # php /path/to/mautic/app/console mautic:campaigns:trigger
    # php /path/to/mautic/app/console mautic:emails:process
    # php /path/to/mautic/app/console mautic:email:fetch
    fabtools.cron.add_task('mautic1', '*/5 * * * *', env.user,
                           'php {}/app/console mautic:segments:update --env=prod'.format(path))
    fabtools.cron.add_task('mautic2', '*/5 * * * *', env.user,
                           'php {}/app/console mautic:campaigns:rebuild --env=prod'.format(path))
    fabtools.cron.add_task('mautic3', '*/5 * * * *', env.user,
                           'php {}/app/console mautic:campaigns:trigger --env=prod'.format(path))
    fabtools.cron.add_task('mautic4', '*/5 * * * *', env.user,
                           'php {}/app/console mautic:emails:process --env=prod'.format(path))
    fabtools.cron.add_task('mautic5', '*/5 * * * *', env.user,
                           'php {}/app/console mautic:email:fetch --env=prod'.format(path))


def setup_prod():
    if fabtools.files.is_dir(path):
        sudo('rm -r ' + path)
    sudo('mkdir -p ' + path)
    with cd(path.parent):
        sudo('chown -R %s:%s %s' % (env.user, env.user, env.project))
    with cd(path):
        run('git clone ' + repo + ' .')
        run('git checkout tags/2.1.1')
        run('composer install')
    with cd(path):
        sudo('mkdir -p ' + path + '/upgrade')

    chown()
    chmod()
    setfacl()
    setup_cronjobs()


def setup_with_apache():
    prepare_apache_server()
    setup_db()
    setup_prod()
    report()


def setup_with_nginx():
    prepare_nginx_server()
    setup_db()
    setup_prod()
    report()


def report():
    run('clear')
    print(green('You can access your site by URL http://%s/ and continue installation using data below' % env.domain))
    print(green('------------------------------------'))
    print('\n')
    print(green('MYSQL database'))
    print(green('------------------------------------'))
    print('Host: %s' % env.db['host'])
    print('Database name: %s' % env.db['name'])
    print('Database root: root')
    print('Database root password: %s' % env.db['root'])
    print('Database user: %s' % env.db['user'])
    print('Database user password: %s' % env.db['pass'])


def destroy_mysql():
    with settings(abort_exception=FabricException):
        try:
            sudo('service mysql stop')  # or mysqld
            sudo('killall -9 mysql')
            sudo('killall -9 mysqld')
        except FabricException:
            pass
    sudo('apt-get -y remove --purge mysql-server mysql-client mysql-common')
    sudo('apt-get -y autoremove')
    sudo('apt-get -y autoclean')
    sudo('deluser mysql')
    sudo('rm -rf /var/lib/mysql')
    sudo('rm -rf /var/log/mysql')
    sudo('rm -rf /etc/mysql')
    sudo('apt-get -y purge mysql-server-core-5.5')
    sudo('apt-get -y purge mysql-client-core-5.5')


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


class RuntimeException(Exception):
    pass


def update_mautic():
    with cd(path):
        # sudo('rm -rf app/cache/*')
        # run('app/console cache:warmup --env=prod')
        run('git reset --hard')
        run('git checkout tags/2.1.1')
        with settings(abort_exception=RuntimeException):
            try:
                run('composer install')
            except RuntimeException:
                sudo('rm -rf app/cache/*')
                run('app/console cache:warmup --env=prod')
                run('composer install')
        # run('php app/console doctrine:migration:status')
        run('php app/console doctrine:migration:migrate')
        setfacl()
        run('php app/console cache:clear --env=prod')
        # run('php app/console mautic:update:find -e prod')
        # run('php app/console mautic:update:apply -e prod --force')


def update_mautic_v2():
    # see docs http://johnlinhart.com/blog/uh-oh-mautic-upgrade-was-not-successful
    # update mautic from v2.1.1 to v2.2.0
    with cd(path):
        sudo('rm -rf app/cache/*')
        sudo('chown -R {}:{} app/cache '.format(env.user, env.user))
        run('php app/console cache:clear')
        with settings(abort_exception=FabricException):
            try:
                sudo('mkdir upgrade')
            except FabricException:
                pass
        sudo('chown -R {}:{} upgrade '.format(env.user, env.user))
        run('php app/console mautic:update:find')
        run('php app/console mautic:update:apply')
        run('php app/console doctrine:migration:status')
        setfacl()
        run('php app/console doctrine:migration:migrate')
        run('php app/console cache:clear --env=prod')
        chown()
        chmod()

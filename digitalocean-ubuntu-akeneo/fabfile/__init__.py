import sys
from fabric.api import *
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
from fabtools.python import virtualenv
from fabtools.system import distrib_codename
import fabtools
from jinja2 import *

root = Path(__file__).ancestor(3)
print(root)
sys.path.append(root)
from worldevops import *

env.project = 'akeneo'
env.http_server = 'apache'  # apache2|nginx
env.install_from = 'git'  # install from git | pip | zip

env.db = {
    'driver': 'pdo_mysql',
    'port': 3306,
    'root': genpass(),
    'name': env.project,
    'user': 'akeneo',
    'pass': genpass(),
    'host': 'localhost',
    'demo': ''  # 'minimal'
}
#  MySQL
# env.db['url'] = 'mysql://%(user)s:%(pass)s@%(host)s:%(port)d/%(name)s' % env.db

#  PostgreSQL
# env.db['driver'] = 'pdo_pgsql'  # you can choose from mysql|postgresql|sqlite
# env.db['port'] = 5432
# env.db['url'] = 'postgres://%(user)s:%(pass)s@%(host)s:%(port)d/%(name)s' % env.db

env.db_str = ''  # db setting string conf file
env.ssl_str = None  # ssl support

env.home = Path('/', 'home', env.user)
env.ssh = '/home/%s/.ssh' % env.user

env.local_root = Path(__file__).ancestor(2)
env.projects_dir = Path('/', 'home', env.user, 'projects')
env.project_dir = Path(env.projects_dir, env.project)
env.docroot = Path(env.project_dir, 'web')
env.downloads = Path('/', 'home', env.user, 'downloaded')

env.site = {
    'domain': env.domain,  # without www.
    'docroot': env.docroot,
    'ssl': False,
    'port': 80,
    'login': 'admin',
    'admin': 'admin@' + env.domain,
    'admin_pwd': genpass(),
    'log_dir': Path(env.projects_dir, 'logs')
}

import random

secret_key = ''.join(
    [random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(50)])

env.app = {
    'host': env.domain,
    'port': 8080,
    'docroot': env.docroot,
    'console': Path(env.project_dir, 'app', 'console'),
    'conf': Path(env.project_dir, 'app', 'config'),
    'secret': secret_key
}

env.mongo = {
    'host': 'localhost',
    'port': 27017,
    'name': 'akeneo'  # database name
}


def setup():
    # fabtools.require.system.locale('en_US.UTF-8')
    # #sudo('apt-get update && apt-get -y dist-upgrade')
    # sudo('apt-get update')
    # fabtools.deb.update_index()
    common_setup()

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
        'libz-dev', 'libpq-dev', 'libyaml-dev', 'curl',
        'php5-cli', 'php5-intl', 'php5-curl',
        'php5-gd', 'php5-mcrypt',
    ])

    make_swap()

    sudo('rm -rf {}'.format(env.projects_dir))
    run('mkdir {}'.format(env.projects_dir))
    run('mkdir {}'.format(env.site['log_dir']))

    setup_http_server()
    setup_db()

    # Require an email server
    fabtools.require.postfix.server(env.domain)
    setup_php()

    # store_git_token()  # this is required for composer, some packages have api limits

    with settings(abort_exception=FabricException):
        try:
            setup_app()
        except FabricException:
            pass

    init_app()
    setup_cronjobs()
    report()

    if env.http_server == 'apache':
        fabtools.require.service.restart('apache2')
    else:
        fabtools.require.service.restart('nginx')


def init_app():
    with cd(env.project_dir):
        sudo('chown -R {}.www-data app/cache'.format(env.user))
        sudo('chown -R {}.www-data app/logs'.format(env.user))
        sudo('chmod -R 0777 app/logs')
        sudo('chown -R 0777 app/logs')

        run('php app/console pim:install --env=prod')
        run('php app/console php --env=prod oro:translation:dump en_US')
        run('php app/console pim:installer:assets')


def setup_cronjobs():
    # # for CE & EE
    # /path/to/php /path/to/pim/root/app/console pim:completeness:calculate --env=prod    # recalculates the products completeness
    # /path/to/php /path/to/pim/root/app/console pim:versioning:refresh --env=prod        # processes pending versions
    # # for EE only
    # /path/to/php /path/to/pim/root/app/console akeneo:rule:run --env=prod               # executes rules on products
    fabtools.cron.add_task('completeness', '*/15 * * * *', env.user,
                           'php {} pim:completeness:calculate --env=prod'.format(env.app['console']))
    fabtools.cron.add_task('completeness', '*/15 * * * *', env.user,
                           'php {} pim:versioning:refresh --env=prod'.format(env.app['console']))


def setup_http_server():
    if env.http_server == 'apache':
        setup_apache()
    if env.http_server == 'nginx':
        setup_nginx()


def setup_apache():
    if fabtools.service.is_running('nginx'):
        fabtools.service.stop('nginx')
    fabtools.require.apache.server()
    fabtools.require.deb.packages(['libapache2-mod-php5'])
    fabtools.require.apache.enable_module('rewrite')

    tpldir = str(Path(env.local_root, 'etc', 'apache'))
    target = Path('/', 'etc', 'apache2', 'sites-available', '{}.conf'.format(env.project))

    context = {
        'domain': env.domain,
        'docroot': env.site['docroot'],
        'log_dir': env.site['log_dir']
    }

    upload_template(
        filename="site.conf",
        destination=target,
        context=context,
        use_jinja=True,
        template_dir=tpldir,
        use_sudo=True
    )
    fabtools.require.apache.enable_site(env.project)


def setup_nginx():
    if fabtools.service.is_running('apache2'):
        fabtools.service.stop('apache2')
    fabtools.require.nginx.server()
    fabtools.require.nginx.proxied_site(
        '127.0.0.1',
        docroot=env.docroot,
        proxy_url='http://{host}:{port}'.format(**env.app)
    )


def setup_composer():
    """@setup git, composer"""
    run('curl -sS https://getcomposer.org/installer | php')
    # sudo('mv composer.phar /usr/local/bin/composer', user=env.user)


def setup_app():
    # Ubuntu 13.10 only
    if distrib_codename() == 'saucy':
        sudo('apt-get install php5-json')
        sudo('ln -s /etc/php5/conf.d/mcrypt.ini /etc/php5/mods-available/')

    sudo('php5enmod mcrypt')

    if distrib_codename() == 'quantal':
        sudo('apt-get install php-apc')
    else:
        sudo('apt-get install php5-apcu')

    with cd(env.projects_dir):
        sudo('rm -rf {}'.format(env.project))
        run('git clone https://github.com/akeneo/pim-community-standard.git {}'.format(env.project))
        with cd(env.project):
            run('git checkout tags/v1.5.0')
            setup_config()
            setup_composer()
            with settings(abort_exception=FabricException):
                try:
                    run('php composer.phar install')
                except FabricException:
                    pass

            run('php app/console cache:clear --env=prod')
            run('php app/console pim:install --env=prod')


def create_admin():
    pass


def setup_php():
    target = str(Path('/', 'etc', 'php5', 'cli'))
    tpldir = str(Path(env.local_root, 'etc', 'php5', 'cli'))
    upload_template(
        filename="php.ini",
        destination=target,
        use_jinja=True,
        template_dir=tpldir,
        use_sudo=True
    )


def setup_config():
    context = {}
    if env.db['driver'] == 'mongo':
        context['mongo'] = env.db_str

    if env.site['ssl'] == True:
        env.ssl_str = """
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True"""

    sudo('rm -f {}'.format(Path(env.app['conf'], 'parameters.yml')))
    sudo('rm -f {}'.format(Path(env.app['conf'], 'pim_parameters.yml')))

    target = Path(env.app['conf'], 'pim_parameters.yml')
    tpldir = str(Path(env.local_root, 'app', 'config'))

    upload_template(
        filename="pim_parameters.yml",
        destination=target,
        context=context,
        use_jinja=True,
        template_dir=tpldir,
        use_sudo=True
    )
    fabtools.require.file(Path(env.app['conf'], 'parameters.yml'), contents=env.db_str)


def setup_db():
    if env.db['driver'] == 'pgsql':
        setup_postgres()

    if env.db['driver'] == 'pdo_mysql':
        setup_mysql()

    if env.db['driver'] == 'mongo':
        setup_mongo()


def reinstall_db():
    run('php app/console pim:installer:db --env=prod')


def setup_postgres():
    with settings(abort_exception=FabricException):
        try:
            fabtools.require.postgres.server()
        except FabricException:
            sudo('apt-get -f -y install')
    fabtools.require.deb.packages(['postgresql-server-dev-9.3', 'postgresql-client'])

    env.db_str = '''
parameters:
    database_driver:   %(driver)s
    database_host:     %(host)s
    database_port:     %(port)s
    database_name:     %(name)s
    database_user:     %(user)s
    database_password: %(pass)s
    locale:            en
    secret:            %(secret)s
    ''' % {
        'driver': env.db['driver'],
        'name': env.db['name'],
        'user': env.db['user'],
        'pass': env.db['pass'],
        'host': env.db['host'] or 'localhost',
        'port': env.db['port'] or 5432,
        'secret': env.app['secret']
    }
    # for minimal install add this after secret
    # installer_data: PimInstallerBundle:minimal
    if env.db['demo'] == 'minimal':
        env.db_str += "\s\s\s\sinstaller_data: PimInstallerBundle:minimal"
        reinstall_db()

    fabtools.require.postgres.user(env.db['user'], env.db['pass'])
    fabtools.require.postgres.database(env.db['name'], owner=env.db['user'])
    print(green('PostgreSQL installed and running.'))


def setup_mysql():
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

    fabtools.require.deb.packages(['php5-mysql', 'libmysqlclient-dev'])
    env.db_str = '''
parameters:
    database_driver:   %(driver)s
    database_host:     %(host)s
    database_port:     %(port)s
    database_name:     %(name)s
    database_user:     %(user)s
    database_password: %(pass)s
    locale:            en
    secret:            %(secret)s
    ''' % {
        'driver': env.db['driver'],
        'name': env.db['name'],
        'user': env.db['user'],
        'pass': env.db['pass'],
        'host': env.db['host'] or 'localhost',
        'port': env.db['port'] or 3306,
        'secret': env.app['secret']
    }
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.user(env.db['user'], env.db['pass'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.database(env.db['name'], owner=env.db['user'])

    fabtools.require.service.started('mysql')
    print(green('MySQL installed and running.'))


def setup_mongo():
    sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv 7F0CEB10')
    sudo(
        'echo deb http://downloads-distro.mongodb.org/repo/debian-sysvinit dist 10gen | sudo tee /etc/apt/sources.list.d/mongodb-10gen.list > /dev/null')
    sudo('apt-get update')
    sudo('apt-get install mongodb-10gen=2.4.14')
    sudo('echo "mongodb-10gen hold" | sudo dpkg --set-selections')
    if distrib_codename() == 'trusty':
        sudo('apt-get install php5-mongo')
    else:
        sudo('apt-get install php-pear build-essential php5-dev')
        sudo('pecl install mongo')
        sudo('echo "extension=mongo.so" | sudo tee /etc/php5/conf.d/mongo.ini > /dev/null')

    with cd('env.project_dir'):
        run('php ../composer.phar --prefer-dist require doctrine/mongodb-odm-bundle 3.0.1')

    # In app/AppKernel.php, uncomment the following line (this will enable DoctrineMongoDBBundle and will load and enable the MongoDB configuration):
    # gedit app/AppKernel.php
    # new Doctrine\Bundle\MongoDBBundle\DoctrineMongoDBBundle(),
    get('app/config/pim_parameters.yml')

    env.db_str = """
    pim_catalog_product_storage_driver: doctrine/mongodb-odm
    mongodb_server: 'mongodb://{host}:{port}'
    mongodb_database: {name}
    """.format(**env.mongo)
    # update parameters and upload back


def report():
    report = []
    report.append("""
    """ % {'domain': env.site['domain']})

    report.append("\n" + 20 * '=' + ' Site ' + 20 * '=')
    dbs = []
    for k, v in env.site.items():
        dbs.append(str(k) + ': ' + str(v))
    report.append("\n".join(dbs))

    report.append("\n" + 20 * '=' + ' Database ' + 20 * '=')
    report.append(env.db['driver'])
    dbs = []
    for k, v in env.db.items():
        dbs.append(str(k) + ': ' + str(v))
    report.append("\n".join(dbs))

    print("\n".join(report))


def setup_mail_server():
    # Require an email server
    fabtools.require.postfix.server(env.domain)


def install_nodejs():
    fabtools.require.deb.packages(["nodejs", 'npm'])
    fabtools.files.symlink(source="/usr/bin/nodejs", destination="/usr/bin/node", use_sudo=True)


def install_grunt():
    sudo("npm install -g grunt-cli")


def install_less():
    sudo("npm install -g less")

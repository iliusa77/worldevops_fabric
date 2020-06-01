# for Ubuntu 14.04
'''
how to run: fab -H demo.loc --user vagrant --password vagrant --set=domain={domain} setup

'''

import os
from fabric.api import *
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
from fabtools.python import virtualenv
from fabtools.system import distrib_codename
import fabtools
from worldevops import *
from jinja2 import *

env.project = 'akeneo'
env.project_dir = Path('/home', env.user, env.project)
select_db = 'mysql'
#select_db = 'mongo' #this feature don't work

env.site = {
    'domain': env.domain,  # without www.
    'docroot': '{}/pim-community-standard/web'.format(env.project_dir),
    'ssl': False,
    'port': 80,
    'login': 'admin',
    'admin': 'admin@' + env.domain,
    'admin_pwd': genpass(),
    'log_dir': Path(env.project_dir, 'logs')
}

env.db = {
    'driver': 'mysql',
    'host': 'localhost',
    'name': 'akeneo_pim',
    'user': 'akeneo_pim',
    'pass': 'akeneo_pim',
    'port': 3306,
    'root': ''
}

env.mongo = {
    'host': 'localhost',
    'port': 27017,
    'name': 'akeneo'  # database name
}


def setup_system():
    sudo('mkdir -p {}/logs'.format(env.project_dir))
    sudo('apt-get update')
    fabtools.require.deb.packages(['sudo'])
    fabtools.require.system.locale('en_US.UTF-8')
    fabtools.deb.update_index()
    fabtools.require.deb.packages([
        'imagemagick', 'libxml2-dev', 'libxml2',
        'libxslt1.1', 'libevent-2.0-5', 'libsasl2-2',
        'libldap-2.4-2', 'python-dev', 'libjpeg-dev',
        'libpcre3', 'libpcre3-dev', 'fail2ban',
        'python-pip', 'python-virtualenv', 'mc',
        'python-unipath', 'git', 'ufw', 'libxslt1-dev',
        'zlib1g-dev', 'libsasl2-dev', 'libldap2-dev', 'libssl-dev',
        'python-pil', 'python-nose', 'libgeos-dev', 'python-lxml',
        'libffi6', 'libffi-dev', 'python-dev', 'htop', 'vim',
        'libz-dev','libpq-dev', 'libyaml-dev', 'curl', 'mysql-server',
        'php5-cli', 'php5-intl', 'php5-curl', 'php5-mysql',
        'php5-gd', 'php5-mcrypt', 'php5-apcu'
    ])
    put('configs/php5/php.ini', '/etc/php5/cli/', use_sudo=True)
    sudo('php5enmod mcrypt')
    sudo('php5enmod intl')
    sudo('php5enmod apcu')
    context = {}
    if env.db['driver'] == 'mongo':
        context['mongo'] = env.db_str
    

def setup_mysql():
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.user(env.db['user'], env.db['pass'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.database(env.db['name'], owner=env.db['user'])
    print(env.db['pass'])

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

    #with cd(env.project_dir):
    #    run('php ../composer.phar --prefer-dist require doctrine/mongodb-odm-bundle 3.0.1')

    # In app/AppKernel.php, uncomment the following line (this will enable DoctrineMongoDBBundle and will load and enable the MongoDB configuration):
    # gedit app/AppKernel.php
    # new Doctrine\Bundle\MongoDBBundle\DoctrineMongoDBBundle(),
    #get('app/configs/pim_parameters.yml')

    env.db_str = """
    pim_catalog_product_storage_driver: doctrine/mongodb-odm
    mongodb_server: 'mongodb://{host}:{port}'
    mongodb_database: {name}
    """.format(**env.mongo)
    # update parameters and upload back

def setup_db():
    if select_db == 'mysql':
        setup_mysql()

    if select_db == 'mongo':
        setup_mongo()

def setup_apache():
    if fabtools.service.is_running('nginx'):
        fabtools.service.stop('nginx')
    fabtools.require.apache.server()
    fabtools.require.deb.packages(['libapache2-mod-php5'])
    fabtools.require.apache.enable_module('rewrite')

    tpldir = str(Path('configs', 'apache'))
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
    sudo('service apache2 restart')


def install_akeneo():
    with cd(env.project_dir):
        sudo('wget http://download.akeneo.com/pim-community-standard-v1.5-latest.tar.gz')
        sudo('tar -xvzf pim-community-standard-v1.5-latest.tar.gz && rm pim-community-standard-v1.5-latest.tar.gz')
    

def setup_akeneo():
    if select_db == 'mysql':
        with cd(env.project_dir):
            sudo('curl -sS https://getcomposer.org/installer | php')
            put('configs/composer.json', '{}'.format(env.project_dir), use_sudo=True)
            with cd(env.project_dir):
                sudo('php composer.phar install')
            with cd('{}/pim-community-standard'.format(env.project_dir)):
                sudo('php app/console cache:clear --env=prod')
                sudo('php app/console pim:install --env=prod')
            sudo('chmod a+w -R {}/pim-community-standard/web'.format(env.project_dir))
            sudo('chmod 777 -R {}/pim-community-standard/app/cache'.format(env.project_dir))
            sudo('chmod 777 -R {}/pim-community-standard/app/logs'.format(env.project_dir))
    if select_db == 'mongo':
        with cd(env.project_dir):
            sudo('curl -sS https://getcomposer.org/installer | php')
            put('configs/composer.json', '{}'.format(env.project_dir), use_sudo=True)
            with cd(env.project_dir):
                sudo('php composer.phar --prefer-dist require doctrine/mongodb-odm-bundle 3.0.1')
                sudo('php composer.phar install')
            with cd('{}/pim-community-standard'.format(env.project_dir)):
                sudo('php app/console cache:clear --env=prod')
                sudo('php app/console pim:install --env=prod')
            sudo('chmod a+w -R {}/pim-community-standard/web'.format(env.project_dir))
            sudo('chmod 777 -R {}/pim-community-standard/app/cache'.format(env.project_dir))
            sudo('chmod 777 -R {}/pim-community-standard/app/logs'.format(env.project_dir))

def report():
    run("clear")
    print(green(
        "-------------------------------------------------------------------------------------------------------------------"))
    print(green("Akeneo been successfully installed, visit http:{}/app.php".format(env.domain)))
    print(green("login: admin"))
    print(green("password: admin"))
    print(green(
        "-------------------------------------------------------------------------------------------------------------------"))


def setup():
    setup_system()
    setup_db()
    install_akeneo()
    setup_akeneo()
    setup_apache()
    report()

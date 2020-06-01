# for CentOS 6.7

import os
from fabric.api import *
from fabric.api import run, sudo, task, get, put
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
from fabtools.python import virtualenv
from fabtools.system import distrib_codename
import fabtools
from worldevops import *

env.project = 'akeneo'
env.project_dir = Path('/', 'var/www', env.project)


def setup_system():
    sudo(
        'wget https://dl.fedoraproject.org/pub/epel/epel-release-latest-6.noarch.rpm && rpm -Uvh epel-release-latest-6.noarch.rpm')
    sudo('wget http://rpms.famillecollet.com/enterprise/remi-release-6.rpm && rpm -Uvh remi-release-6*.rpm')
    put('configs/remi.repo', '/etc/yum.repos.d/', use_sudo=True)
    sudo(
        'yum install -y httpd mod_ssl php php-mysql php-devel php-gd php-pecl-memcache php-pspell php-snmp php-xmlrpc php-xml php-pear php-devel php-mcrypt php-intl php-pecl-apc httpd-devel pcre-devel gcc make mysql-server')
    put('configs/php.ini', '/etc/', use_sudo=True)
    put('configs/httpd.conf', '/etc/httpd/conf/', use_sudo=True)
    sudo('echo "/usr/lib64/php/modules/mcrypt.so" >> /etc/php.d/mcrypt.ini')
    sudo('echo "/usr/lib64/php/modules/intl.so" >> /etc/php.d/intl.ini')
    sudo('echo "/usr/lib64/php/modules/apcu.so" >> /etc/php.d/apcu.ini')
    sudo('/sbin/chkconfig httpd on && /usr/sbin/apachectl start')
    sudo('service iptables stop && chkconfig iptables off')
    sudo('chkconfig mysqld on && service mysqld start')


def add_db():
    sudo('mkdir -p {}'.format(env.project_dir))
    put('configs/add_db.sh', '{}'.format(env.project_dir), use_sudo=True)
    sudo('chmod a+x {}/add_db.sh'.format(env.project_dir))
    sudo('/bin/bash {}/add_db.sh'.format(env.project_dir))
    sudo('rm -f {}/add_db.sh'.format(env.project_dir))


def install_akeneo():
    with cd(env.project_dir):
        sudo('wget http://download.akeneo.com/pim-community-standard-v1.5-latest.tar.gz')
        sudo('tar -xvzf pim-community-standard-v1.5-latest.tar.gz && rm pim-community-standard-v1.5-latest.tar.gz')
    sudo('chmod 777 {}/pim-community-standard/app/cache'.format(env.project_dir))
    sudo('chmod 777 {}/pim-community-standard/app/logs'.format(env.project_dir))


def setup_akeneo():
    with cd(env.project_dir):
        sudo('curl -sS https://getcomposer.org/installer | php')
    put('configs/composer.json', '{}'.format(env.project_dir), use_sudo=True)
    with cd(env.project_dir):
        sudo('php composer.phar install')
    with cd('{}/pim-community-standard'.format(env.project_dir)):
        sudo('php app/console cache:clear --env=prod')
        sudo('php app/console pim:install --env=prod')


def setup_httpd():
    sudo('chown -R apache:apache /var/www/{}'.format(env.project))
    sudo('apachectl -k stop')
    sudo('/etc/init.d/httpd start')


def report():
    run("clear")
    print(green(
        "-------------------------------------------------------------------------------------------------------------------"))
    print(green("Akeneo been successfully installed, visit http:akeneo33.com/app.php"))
    print(green("login: admin"))
    print(green("password: admin"))
    print(green(
        "-------------------------------------------------------------------------------------------------------------------"))


def setup():
    setup_system()
    add_db()
    install_akeneo()
    setup_akeneo()
    setup_httpd()
    report()

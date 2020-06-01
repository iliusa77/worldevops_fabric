import os
from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path
from contextlib import contextmanager
from fabric.contrib.files import exists
from fabric.contrib.files import upload_template
from fabric.api import settings
from fabric.colors import green, yellow


# from fab_deploy import utils

class FabricException(Exception):
    pass


# the servers where the commands are executed
# the user to use for the remote commands
# env.hosts = ['192.168.88.88']
# env.user = 'vagrant'

MYSQL_CREATE_USER = """CREATE USER '%(db_user)s'@'localhost' IDENTIFIED BY '%(db_password)s';"""

MYSQL_CREATE_DB = """CREATE DATABASE %(db_name)s DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;"""

MYSQL_GRANT_PERMISSIONS = """
GRANT ALL ON %(db_name)s.* TO '%(db_user)s'@'localhost';
FLUSH PRIVILEGES;
"""

MYSQL_USER_EXISTS = "SHOW GRANTS FOR '%(db_user)s'@localhost"

env.hosts = ['demo.loc']
env.db = {
    'host': 'localhost',
    'name': 'symfony',
    'login': 'sfuser',
    'pass': 'sfuser_pwd',
    'port': 3306
}

env.conf = {'DB_PASSWD': 'rootpwd'}
env.project = 'symfony'
env.ssh = '/home/%s/.ssh' % env.user

repo = 'https://github.com/symfony/symfony-standard.git'
env.home = Path('/', 'home', env.user)
path = Path(env.home, env.project)
# path = Path('/', 'home', 'vagrant', env.project)


# check read-access to the keys, to be server-independent
# keys = ['~/.ssh/id_rsa']
# env.key_filename = [key for key in keys if os.access(key, os.R_OK)]

def setup_tools():
    """@setup git, composer"""
    if not _git_is_installed():
        sudo('apt-get install -y git')
        print(green('GIT installed'))
    else:
        print(green('GIT already installed'))
    if not _composer_is_installed():
        sudo('curl -sS https://getcomposer.org/installer | php')
        sudo('mv composer.phar /usr/local/bin/composer')
        print(green('Composer installed'))
    else:
        print(green('Composer already installed'))


def setup_nginx():
    """@setup nginx"""
    if not _nginx_is_installed():
        sudo('apt-get install -y nginx')
        print(green('Nginx installed'))
    else:
        print(green('Nginx already installed'))


def setup_mysql():
    """@setup mysql"""
    if not _mysql_is_installed():
        if 'DB_PASSWD' in env.conf:
            passwd = env.conf['DB_PASSWD']
        else:
            passwd = prompt('Please enter MySQL root password:')
        debconf_defaults = [
            "mysql-server-5.6 mysql-server/root_password password %s" % passwd,
            "mysql-server-5.6 mysql-server/root_password_again password %s" % passwd,
        ]
        sudo("echo '%s' | debconf-set-selections" % "\n".join(debconf_defaults))
        warn(yellow('The password for mysql "root" user will be set to "%s"' % passwd))
        sudo('apt-get -y install mysql-server-5.6')
        sudo('apt-get -y install php5-mysql')
        print(green('MySQL installed'))
    else:
        print(green('MySQL already installed'))


def setup_php():
    """@setup phpfpm"""
    if not _php_is_installed():
        sudo('apt-get install -y php5-fpm')
        sudo('apt-get install -y php5-cli')
        print(green('PHP installed'))
    else:
        print(green('PHP already installed'))


def setup_symfony():
    sudo('mkdir -p ' + path)
    with cd(path):
        sudo('git clone ' + repo + ' .')
        sudo("git checkout 2.8")
        sudo('composer -n install')
        sudo('chmod -R 777 app/cache')
        sudo('chmod -R 777 app/logs')
    setup_db()
    upload_db_config()
    with cd(path):
        sudo('php app/console doctrine:schema:create')


def _mysql_user_exists(db_user):
    sql = MYSQL_USER_EXISTS % dict(db_user=db_user)
    with settings(hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True):
        result = sudo('echo "%s" | mysql --user="%s" --password="%s"' % (sql, 'root', env.conf['DB_PASSWD']))
    return result.succeeded


def mysql_create_user():
    """Creates mysql user."""
    if _mysql_user_exists(env.db['login']):
        puts('User %s already exists' % env.db['login'])
        return
    sql = MYSQL_CREATE_USER % dict(db_user=env.db['login'], db_password=env.db['pass'])
    sudo('echo "%s" | mysql --user="%s" --password="%s"' % (sql, 'root', env.conf['DB_PASSWD']))


def setup_db():
    """Setup database"""
    sudo('echo "%s" | mysql --user="%s" --password="%s"' % (
    'DROP DATABASE IF EXISTS %s' % env.db['name'], 'root', env.conf['DB_PASSWD']))
    sql = MYSQL_CREATE_DB % dict(db_name=env.db['name'])
    sudo('echo "%s" | mysql --user="%s" --password="%s"' % (sql, 'root', env.conf['DB_PASSWD']))
    mysql_create_user()
    mysql_grant_permissions()


def mysql_grant_permissions():
    """Grants all permissions"""
    sql = MYSQL_GRANT_PERMISSIONS % dict(db_name=env.db['name'], db_user=env.db['login'])
    # print(sql)
    # mysql_execute(sql, 'root')


def _nginx_is_installed():
    with settings(hide('stderr'), warn_only=True):
        output = run('nginx -v')
    return output.succeeded


def _mysql_is_installed():
    with settings(hide('stderr'), warn_only=True):
        output = run('mysql --version')
    return output.succeeded


def _php_is_installed():
    with settings(hide('stderr'), warn_only=True):
        output = run('php --version')
    return output.succeeded


def _git_is_installed():
    with settings(hide('stderr'), warn_only=True):
        output = run('git --version')
    return output.succeeded


def _composer_is_installed():
    with settings(hide('stderr'), warn_only=True):
        output = run('composer --version')
    return output.succeeded


def setup_nginx_config():
    with open('./nginx/symfony.conf') as fn:
        config_tpl = fn.read()
    require.nginx.site(
        env.project,
        template_contents=config_tpl,
        port=80,
        domain=env.project,
        path=path
    )
    require.nginx.enabled(env.project)


def upload_db_config():
    upload_template(
        './config/parameters.yml',
        Path(path, 'app', 'config'),
        use_sudo=True,
        context={'db_host': env.db['host'], 'db_port': env.db['port'], 'db_name': env.db['name'],
                 'db_user': env.db['login'], 'db_password': env.db['pass']}
    )
    print(green('Done'))


def setup_prod():
    sudo('apt-get update')
    sudo('apt-get -y dist-upgrade')
    setup_nginx()
    setup_mysql()
    setup_php()
    restart_services()
    setup_tools()
    setup_symfony()
    install_less()
    print(green('Done'))
    setup_nginx_config()


def restart_services():
    sudo("service mysql restart")
    sudo("service nginx reload")
    sudo("service nginx restart")


def clear_cache():
    with cd(path):
        sudo("rm -R app/cache/*")
        sudo('chmod -R 777 app/cache/*')


def install_less():
    require.deb.packages(["nodejs", 'npm'])
    fabtools.files.symlink(source="/usr/bin/nodejs", destination="/usr/bin/node", use_sudo=True)
    sudo("npm install -g less")

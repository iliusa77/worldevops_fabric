from fabric.api import *
from fabric.api import settings
import fabtools


def fix_dpkg():
    sudo('apt-get -y -f install')

def setup_system():
	sudo('apt-get update')
	fabtools.require.deb.packages([
        'build-essential', 'software-properties-common', 'software-properties-common',
        'curl', 'git-core', 'libxml2-dev', 'libxslt1-dev', 'libfreetype6-dev', 'python',
        'python-pip', 'python-apt', 'python-dev', 'libxmlsec1-dev', 'swig', 'libmysqlclient-dev'
    ])

def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))


class FabricException(Exception):
    pass


def store_git_token():
    fabtools.require.file('/home/vagrant/.composer/auth.json', contents="cde24ad140c969c5264b8e2ef1cdebc2c059d4e6")


def create_app_user(user, passwd):
    print('Create application user {0} with password {1} at {2}'.format(user, passwd, env.host_string))
    fabtools.require.user(user, password=passwd, create_home=True)
    fabtools.require.users.sudoer(user, hosts='ALL', operators='ALL', passwd=False, commands='ALL')


def install_mysql():
    with settings(abort_exception=FabricException):
        try:
            fabtools.require.mysql.server(password=env.db['root'])
        except FabricException:
            sudo('apt-get -f -y install')

    fabtools.require.deb.packages(['libmysqlclient-dev'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.user(env.db['user'], env.db['pass'])
        fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.database(env.db['name'], owner=env.db['user'])


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


def destroy_apache():
    fabtools.service.stop('apache2')
    fabtools.deb.uninstall(['apache2'], purge=True, options=None)
    sudo('rm -f /etc/apache2/sites-available/*')
    sudo('rm -f /etc/apache2/sites-enabled/*')
    # sudo('apt-get purge apache2*')


def destroy_nginx():
    fabtools.service.stop('nginx')
    fabtools.deb.uninstall(['nginx'], purge=True, options=None)
    sudo('rm -f /etc/nginx/sites-available/*')
    sudo('rm -f /etc/nginx/sites-enabled/*')


def destroy_supervisor():
    fabtools.service.stop('supervisor')
    fabtools.deb.uninstall(['supervisor'], purge=True, options=None)
    sudo('apt-get purge supervisor*')
    # sudo('apt-get -y  remove supervisor')
    # sudo('apt-get -y  --purge remove supervisor\*')


def destroy_all():
    with settings(abort_exception=FabricException):
        try:
            destroy_supervisor()
        except FabricException:
            pass
    with settings(abort_exception=FabricException):
        try:
            destroy_mysql()
        except FabricException:
            pass
    with settings(abort_exception=FabricException):
        try:
            destroy_postgresql()
        except FabricException:
            pass

    destroy_nginx()

    with settings(abort_exception=FabricException):
        try:
            destroy_apache()
        except FabricException:
            pass
    sudo('rm -rf %s' % env.projects_dir)


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

    report.append("\n" + 20 * '=' + ' Cache server ' + 20 * '=')
    report.append(env.cache_server)
    dbs = []
    for k, v in env.redis.items():
        dbs.append(str(k) + ': ' + str(v))
    report.append("\n".join(dbs))
    print("\n".join(report))


def restart_services():
    if env.http_server == 'apache2':
        sudo('service nginx stop')
        fabtools.require.service.restarted('apache2')
    else:
        with settings(abort_exception=FabricException):
            try:
                sudo('killall uwsgi')
            except FabricException:
                pass
        fabtools.require.service.restarted('nginx')
        fabtools.require.service.restarted('supervisor')

        if env.cache_server == 'redis':
            fabtools.require.service.restarted('redis-server')

        if env.cache_server == 'memcache':
            fabtools.require.service.restarted('memcached')

        if env.db['driver'] == 'mysql':
            fabtools.require.service.restarted('mysql-server')

        if env.db['driver'] == 'pgsql':
            fabtools.require.service.restarted('postgresql')


def setup_mail_server():
    # Require an email server
    fabtools.require.postfix.server(env.domain)


def setup_firewall():
    sudo('ufw default deny incoming')
    sudo('ufw default deny outgoing')
    #sudo('ufw allow ssh')
    sudo('ufw allow  from 89.28.84.116 to any port 22')
    sudo('ufw allow from 89.28.0.0/24 to any port 22')
    #sudo('ufw allow 8069/tcp')
    #sudo('ufw allow 80/tcp')
    #sudo('ufw allow ftp')
    sudo('ufw allow 21/tcp')
    sudo('ufw allow www')
    sudo('ufw allow http')
    sudo('ufw allow https')

    # email
    # To allow your server to respond to SMTP connections, port 25, run this command
    sudo('ufw allow 25')

    # To allow your server to respond to IMAP connections, port 143, run this command
    sudo('ufw allow 143')

    # Note: It is common for SMTP servers to use port 587 for outbound mail.
    sudo('ufw allow 587')

    # To allow your server to respond to IMAPS connections, port 993, run this command
    sudo('ufw allow 993')

    # To allow your server to respond to POP3 connections, port 110, run this command
    sudo('ufw allow 110')

    # To allow your server to respond to POP3S connections, port 995, run this command
    sudo('ufw allow 995')

    # required for system updates
    sudo('ufw allow out 53,67,68/udp')
    sudo('ufw allow out 53/tcp')

    sudo('ufw enable')
    sudo('ufw status verbose')



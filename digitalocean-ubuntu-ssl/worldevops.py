from fabric.api import *
from fabric.api import settings
import fabtools


def fix_dpkg():
    sudo('apt-get -y -f install')


def common_setup():

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
        'libz-dev','libpq-dev', 'libyaml-dev', 'curl',
        'php5-cli', 'php5-intl', 'php5-curl',
        'php5-gd', 'php5-mcrypt',
    ])


def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))


def gensecret():
    import random
    return ''.join(
        [random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])

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


def install_postgresql():
    with settings(abort_exception=FabricException):
        try:
            fabtools.require.postgres.server()
        except FabricException:
            sudo('apt-get -f -y install')

    fabtools.require.deb.packages(['postgresql-server-dev-9.3', 'postgresql-client'])

    fabtools.require.postgres.user(env.db['user'], env.db['pass'])
    fabtools.require.postgres.database(env.db['name'], owner=env.db['user'])



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
    sudo('ufw allow  from 11.22.33.44 to any port 22')
    sudo('ufw allow from 11.22.0.0/24 to any port 22')
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


def setup_wkhtml2pdf():
    with cd('/tmp'):
        sudo('wget http://download.gna.org/wkhtmltopdf/0.12/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb')
        sudo('dpkg -i wkhtmltox-0.12.1_linux-trusty-amd64.deb')
        sudo('cp /usr/local/bin/wkhtmltopdf /usr/bin')
        sudo('cp /usr/local/bin/wkhtmltoimage /usr/bin')


"""

You can do a couple of things for avoiding this. Setting the DEBIAN_FRONTEND variable to noninteractive and using -y flag. For example:

export DEBIAN_FRONTEND=noninteractive
apt-get -y install [packagename]
If you need to install it via sudo, use:

sudo DEBIAN_FRONTEND=noninteractive apt-get -y install [packagename]

"""


def make_swap():
    """
    When composer requires more memory add swap of 2G
    """
    with settings(abort_exception=FabricException):
        try:
            sudo('/sbin/swapoff /var/swap.1')
        except FabricException:
            pass

    sudo('/bin/dd if=/dev/zero of=/var/swap.1 bs=1M count=4194')
    sudo('/sbin/mkswap /var/swap.1')
    sudo('/sbin/swapon /var/swap.1')


def create_user_and_database(root_pwd, db, owner):
    with settings(mysql_user='root', mysql_password=root_pwd):
        fabtools.require.mysql.user(owner, owner)
    with settings(mysql_user='root', mysql_password=root_pwd):
        fabtools.require.mysql.database(db, owner=owner)


def install_nodejs(version=4):
    #fabtools.require.deb.packages(["nodejs", 'npm'])
    #Optional: install build tools
    sudo('apt-get install -y build-essential')

    if version == 4:
        sudo('curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -')
    else:
        #Alternatively, for Node.js v6:
        sudo('curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -')

    sudo('apt-get install -y nodejs')
    #To compile and install native addons from npm you may also need to install build tools:
    fabtools.files.symlink(source="/usr/bin/nodejs", destination="/usr/bin/node", use_sudo=True)


def install_grunt():
    sudo("npm install -g grunt")


def install_less():
    sudo("npm install -g less")

def setup_fail2ban_ssh():
    sudo('apt-get update && apt-get install fail2ban -y')
    put(local_path="configs/fail2ban/ssh.local", remote_path="/etc/fail2ban/jail.d/", use_sudo=True)
    run('sudo service fail2ban restart && sudo fail2ban-client reload ssh && sudo fail2ban-client reload ssh-ddos')

def setup_fail2ban_apache():
    sudo('apt-get update && apt-get install fail2ban -y')
    put(local_path="configs/fail2ban/apache.local", remote_path="/etc/fail2ban/jail.d/", use_sudo=True)
    run('sudo service fail2ban restart && sudo fail2ban-client reload ssh && sudo fail2ban-client reload ssh-ddos && sudo fail2ban-client reload apache')

def setup_fail2ban_nginx():
    sudo('apt-get update && apt-get install fail2ban -y')
    put(local_path="configs/fail2ban/nginx.local", remote_path="/etc/fail2ban/jail.d/", use_sudo=True)
    run('sudo service fail2ban restart && sudo fail2ban-client reload ssh && sudo fail2ban-client reload ssh-ddos && sudo fail2ban-client reload nginx-http-auth')

def setup_fail2ban_mysql():
    sudo('apt-get update && apt-get install fail2ban -y')
    put(local_path="configs/fail2ban/mysql.local", remote_path="/etc/fail2ban/jail.d/", use_sudo=True)
    run('sudo service fail2ban restart && sudo fail2ban-client reload ssh && sudo fail2ban-client reload ssh-ddos && sudo fail2ban-client reload mysqld-auth')

def setup_fail2ban_apachemysql():
    sudo('apt-get update && apt-get install fail2ban -y')
    put(local_path="configs/fail2ban/apachemysql.local", remote_path="/etc/fail2ban/jail.d/", use_sudo=True)
    run('sudo service fail2ban restart && sudo fail2ban-client reload ssh && sudo fail2ban-client reload ssh-ddos && sudo fail2ban-client reload apache && sudo fail2ban-client reload mysqld-auth')



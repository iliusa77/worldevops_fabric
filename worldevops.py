from fabric.api import *
from fabric.api import settings
import fabtools
from unipath import Path
import os
if  'WORLDEVOPS_PATH' not in os.environ:
    raise Exception("WORLDEVOPS_PATH is not set. add export WORLDEVOPS_PATH='/home/user/worldevops_fabric' in ~/.bashrc")
# for solving "WORLDEVOPS_PATH is not set." add export WORLDEVOPS_PATH='/home/user/worldevops_fabri' in ~/.bashrc 


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
        'libz-dev', 'libpq-dev', 'libyaml-dev', 'curl',
        'php5-cli', 'php5-intl', 'php5-curl',
        'php5-gd', 'php5-mcrypt', 'systemctl'
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
    # sudo('ufw allow ssh')
    sudo('ufw allow  from 89.28.84.116 to any port 22')
    sudo('ufw allow from 89.28.0.0/24 to any port 22')
    # sudo('ufw allow 8069/tcp')
    # sudo('ufw allow 80/tcp')
    # sudo('ufw allow ftp')
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
    # fabtools.require.deb.packages(["nodejs", 'npm'])
    # Optional: install build tools
    sudo('apt-get install -y build-essential')

    if version == 4:
        sudo('curl -sL https://deb.nodesource.com/setup_4.x | sudo -E bash -')
    else:
        # Alternatively, for Node.js v6:
        sudo('curl -sL https://deb.nodesource.com/setup_6.x | sudo -E bash -')

    sudo('apt-get install -y nodejs')
    # To compile and install native addons from npm you may also need to install build tools:
    fabtools.files.symlink(source="/usr/bin/nodejs", destination="/usr/bin/node", use_sudo=True)


def setup_static(static_dir):
    sudo('apt-get -y install npm')
    sudo('npm install npm -g')
    sudo('npm install gulp -g')
    sudo('apt-get install nodejs-legacy')
    with cd(static_dir):
        run('npm install --save')
        run('npm start')


def update_static(static_dir):
    with cd(static_dir):
        run('npm install')
        run('npm start')


def upgrade_nodejs():
    sudo('apt-get install nodejs-legacy')
    sudo('npm cache clean -f')
    sudo('npm install -g n')
    sudo('n stable')
    # sudo('ln -sf /usr/local/n/versions /node/<VERSION>/bin/node/usr/bin/node')
    # sudo('n latest')


def install_grunt():
    sudo("npm install -g grunt")


def install_less():
    sudo("npm install -g less")


def setup_fail2ban_ssh():
    sudo('apt-get update && apt-get install fail2ban -y')
    source = Path(os.environ.get('HOURLIES_PATH'), 'configs', 'fail2ban', 'ssh.local')
    put(local_path=source, remote_path="/etc/fail2ban/jail.d/", use_sudo=True)
    run('sudo service fail2ban restart && sudo fail2ban-client reload ssh && sudo fail2ban-client reload ssh-ddos')


def setup_fail2ban_apache():
    sudo('apt-get update && apt-get install fail2ban -y')
    source = Path(os.environ.get('HOURLIES_PATH'), 'configs', 'fail2ban', 'apache.local')
    put(local_path=source, remote_path="/etc/fail2ban/jail.d/", use_sudo=True)
    run(
        'sudo service fail2ban restart && sudo fail2ban-client reload ssh && sudo fail2ban-client reload ssh-ddos && sudo fail2ban-client reload apache')


def setup_fail2ban_nginx():
    sudo('apt-get update && apt-get install fail2ban -y')
    source = Path(os.environ.get('HOURLIES_PATH'), 'configs', 'fail2ban', 'nginx.local')
    put(local_path=source, remote_path="/etc/fail2ban/jail.d/", use_sudo=True)
    run(
        'sudo service fail2ban restart && sudo fail2ban-client reload ssh && sudo fail2ban-client reload ssh-ddos && sudo fail2ban-client reload nginx-http-auth')


def setup_fail2ban_mysql():
    sudo('apt-get update && apt-get install fail2ban -y')
    source = Path(os.environ.get('HOURLIES_PATH'), 'configs', 'fail2ban', 'mysql.local')
    put(local_path=source, remote_path="/etc/fail2ban/jail.d/", use_sudo=True)
    run(
        'sudo service fail2ban restart && sudo fail2ban-client reload ssh && sudo fail2ban-client reload ssh-ddos && sudo fail2ban-client reload mysqld-auth')


def setup_fail2ban_apachemysql():
    sudo('apt-get update && apt-get install fail2ban -y')
    source = Path(os.environ.get('HOURLIES_PATH'), 'configs', 'fail2ban', 'apachemysql.local')
    put(local_path=source, remote_path="/etc/fail2ban/jail.d/", use_sudo=True)
    run(
        'sudo service fail2ban restart && sudo fail2ban-client reload ssh && sudo fail2ban-client reload ssh-ddos && sudo fail2ban-client reload apache && sudo fail2ban-client reload mysqld-auth')


def setup_composer():
    """@setup git, composer"""
    sudo('curl -sS https://getcomposer.org/installer | php')
    sudo('mv composer.phar /usr/local/bin/composer')


def setfacl():
    require.deb.packages([
        'acl',
    ])
    fabtools.require.file('{}/setfacl.sh'.format(env.project), """\
#!/bin/sh
HTTPDUSER=`ps aux | grep -E '[a]pache|[h]ttpd|[_]www|[w]ww-data|[n]ginx' | grep -v root | head -1 | cut -d\  -f1`;
sudo setfacl -R -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX {0}/app/cache {0}/app/logs;
sudo setfacl -dR -m u:"$HTTPDUSER":rwX -m u:`whoami`:rwX {0}/app/cache {0}/app/logs;
""".format(env.project))
    run('chmod u+x {}/setfacl.sh'.format(env.project))
    run('/bin/sh {}/setfacl.sh'.format(env.project))
    run('rm {}/setfacl.sh'.format(env.project))


def setup_docker():
    # this setup is divided into two parts
    # second parts should be started manually by enter following command:
    # fab continue_setup
    print(">>>>>>>>>   Setup docker phase 1. ")
    sudo('sudo apt-get update')
    sudo('sudo apt-get -y install apt-transport-https ca-certificates')
    sudo(
        'sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D')

    # On Ubuntu Precise 12.04(LTS)
    if distrib_codename() == 'precise':
        out = 'deb https://apt.dockerproject.org/repo ubuntu-precise main'

    # On Ubuntu Trusty 14.04(LTS)
    if distrib_codename() == 'trusty':
        out = 'deb https://apt.dockerproject.org/repo ubuntu-trusty main'

    # Ubuntu Wily 15.10
    if distrib_codename() == 'wily':
        out = 'deb https://apt.dockerproject.org/repo ubuntu-wily main'

    # Ubuntu Xenial 16.04(LTS)
    if distrib_codename() == 'xenial':
        out = 'deb https://apt.dockerproject.org/repo ubuntu-xenial main'

    # On Debian Wheezy
    if distrib_codename() == 'wheezy':
        out = 'deb https://apt.dockerproject.org/repo debian-wheezy main'

    # On Debian Jessie
    if distrib_codename() == 'jessie':
        out = 'deb https://apt.dockerproject.org/repo debian-jessie main'

    # On Debian Stretch/Sid
    if distrib_codename() == 'sid':
        out = 'deb https://apt.dockerproject.org/repo debian-stretch main'

    print('Distro %s' % out)
    sudo('echo ' + out + ' > /etc/apt/sources.list.d/docker.list')

    with settings(abort_exception=FabricException):
        try:
            sudo('apt-get update && apt-get purge lxc-docker')
        except FabricException:
            pass
    sudo('apt-cache policy docker-engine')
    sudo('apt-get -y install linux-image-extra-$(uname -r)')
    sudo('reboot')


def continue_setup():
    sudo('apt-get update')
    sudo('apt-get -y install docker-engine')

    with settings(abort_exception=FabricException):
        try:
            sudo('service docker start')
        except FabricException:
            pass

    sudo('docker run hello-world')

    with settings(abort_exception=FabricException):
        try:
            sudo('groupadd docker')
        except FabricException:
            pass

    with settings(abort_exception=FabricException):
        try:
            sudo('usermod -aG docker ubuntu && docker run hello-world')
        except FabricException:
            pass
    sudo('echo GRUB_CMDLINE_LINUX="cgroup_enable=memory swapaccount=1" >> /etc/default/grub')
    sudo('update-grub')
    sudo('sudo ufw status')
    sudo('echo DEFAULT_FORWARD_POLICY="ACCEPT" >> /etc/default/ufw')
    sudo('ufw reload')
    sudo('ufw allow 2375/tcp')
    sudo('echo \'DOCKER_OPTS="--dns 8.8.8.8 --dns 192.168.1.1"\' >> /etc/default/docker')
    with settings(abort_exception=FabricException):
        try:
            sudo('restart docker')
        except FabricException:
            pass
    sudo('systemctl enable docker')


def test():
    sudo('echo \'DOCKER_OPTS="--dns 8.8.8.8 --dns 192.168.1.1"\' >> /etc/default/docker')


def uninstall():
    sudo('apt-get -y purge docker-engine')
    sudo('apt-get -y autoremove')
    sudo('rm -rf /var/lib/docker')


def upgrade():
    sudo('apt-get -y upgrade docker-engine')


def setup_sphinx_docker():
    run('git clone https://github.com/stefobark/sphinxdocker')

def system_timezone():
    sudo('timedatectl set-timezone {}'.format(env.timezone))
    sudo('cat /etc/timezone')

def php_timezone():
    sudo('echo "date.timezone = "{}"" >> /etc/php5/cli/php.ini'.format(env.timezone))
    sudo('echo "date.timezone = "{}"" >> /etc/php5/apache2/php.ini'.format(env.timezone))
    sudo('service apache2 restart')
    sudo('cat /etc/php5/cli/php.ini | grep date.timezone')
    sudo('cat /etc/php5/apache2/php.ini | grep date.timezone')

def setup_php_mail():
    sudo('sudo apt-get install sendmail -y')
    sudo('echo "sendmail_path = /usr/sbin/sendmail -t -i" >> /etc/php5/cli/php.ini')
    sudo('sudo service php5-fpm restart')

def install_varnish():
    sudo('apt-get install apt-transport-https && \
        apt-get install curl && \
        curl https://repo.varnish-cache.org/ubuntu/GPG-key.txt | apt-key add - && \
        echo "deb https://repo.varnish-cache.org/ubuntu/ trusty varnish-4.0" >> /etc/apt/sources.list.d/varnish-cache.list && \ && \
        apt-get update && \
        apt-get install varnish && \
        sed -E -i "s/Listen 127.0.0.1:80/Listen 127.0.0.1:8080/"/etc/apache2/ports.conf')
    put('../configs/varnish/default.vcl', '/etc/varnish/default.vcl', use_sudo=True)
    sudo('service apache2 reload && \
        service varnish restart &&')

def remove_varnish():
    sudo('service varnish stop')
    sudo('apt-get remove --purge varnish -y')

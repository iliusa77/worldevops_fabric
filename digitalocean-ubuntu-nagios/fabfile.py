"""
command format  fab -H demo.loc --user vagrant --password vagrant --set=ip=192.168.33.10,domain=demo.loc

"""
from fabric.api import *
from fabric.contrib.files import uncomment
from fabtools import require
import fabtools
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green


class FabricException(Exception):
    pass


def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))

env.project = 'nagios'

#  MySQL
env.db = {
    'root': genpass()
}

env.nagios = {
    'ip': env.ip,  # change to your server IP
    'user': env.project,
    'password': genpass(),
    'email': 'admin@'+ env.domain
}


def setup():
    sudo('apt-get update && apt-get -y dist-upgrade')
    require.apache.server()
    require.mysql.server(password=env.db['root'])
    require.deb.packages([
        'php5',
        'php5-cli',
        'php5-mysql',
        'build-essential',
        'libgd2-xpm-dev',
        'openssl',
        'libssl-dev',
        'xinetd',
        'apache2-utils',
        'unzip'
    ])
    sudo('useradd nagios')
    sudo('groupadd nagcmd')
    sudo('usermod -a -G nagcmd nagios')
    run('curl -L -O https://assets.nagios.com/downloads/nagioscore/releases/nagios-4.1.1.tar.gz')
    run('tar xvf nagios-*.tar.gz')
    with cd('nagios-*'):
        run('./configure --with-nagios-group=nagios --with-command-group=nagcmd')
        run('make all')
        sudo('make install')
        sudo('make install-commandmode')
        sudo('make install-init')
        sudo('make install-config')
        sudo('/usr/bin/install -c -m 644 sample-config/httpd.conf /etc/apache2/sites-available/nagios.conf')
    sudo('usermod -G nagcmd www-data')
    run('curl -L -O http://nagios-plugins.org/download/nagios-plugins-2.1.1.tar.gz')
    run('tar xvf nagios-plugins-*.tar.gz')
    with cd('nagios-plugins-*'):
        run('./configure --with-nagios-user=nagios --with-nagios-group=nagios --with-openssl')
        run('make')
        sudo('make install')
    run('curl -L -O http://downloads.sourceforge.net/project/nagios/nrpe-2.x/nrpe-2.15/nrpe-2.15.tar.gz')
    run('tar xvf nrpe-*.tar.gz')
    with cd('nrpe-*'):
        run(
            './configure --enable-command-args --with-nagios-user=nagios --with-nagios-group=nagios --with-ssl=/usr/bin/openssl --with-ssl-lib=/usr/lib/x86_64-linux-gnu')
        run('make all')
        sudo('make install')
        sudo('make install-xinetd')
        sudo('make install-daemon-config')
    upload_template(
        './config/nrpe/nrpe',
        '/etc/xinetd.d',
        use_sudo=True,
        context={'ip': env.nagios['ip']}
    )
    fabtools.service.restart('xinetd')
    uncomment(Path('/', 'usr', 'local', 'nagios', 'etc', 'nagios.cfg'), '^#cfg_dir=\/usr\/local\/nagios\/etc\/servers',
              use_sudo=True)
    sudo('mkdir /usr/local/nagios/etc/servers')
    upload_template(
        './config/nagios/contacts.cfg',
        Path('/', 'usr', 'local', 'nagios', 'etc', 'objects'),
        use_sudo=True,
        context={'email': env.nagios['email']}
    )
    put('./config/nagios/commands.cfg', Path('/', 'usr', 'local', 'nagios', 'etc', 'objects'), use_sudo=True)
    sudo('a2enmod rewrite')
    sudo('a2enmod cgi')
    sudo('htpasswd -c -b /usr/local/nagios/etc/htpasswd.users %s %s' % (env.nagios['user'], env.nagios['password']))
    upload_template(
        './config/nagios/cgi.cfg',
        Path('/', 'usr', 'local', 'nagios', 'etc'),
        use_sudo=True,
        context={'name': env.nagios['user']}
    )
    sudo('ln -s /etc/apache2/sites-available/nagios.conf /etc/apache2/sites-enabled/')
    fabtools.service.start('nagios')
    fabtools.service.restart('apache2')
    sudo('ln -s /etc/init.d/nagios /etc/rcS.d/S99nagios')
    report()


def report():
    print(green('Nagios is installed'))
    print('You can access it http://server_ip/nagios')
    print('Login: %s' % env.nagios['user'])
    print('Password: %s' % env.nagios['password'])
    print('E-mail: %s' % env.nagios['email'])

from fabric.api import *
from fabric.contrib.files import *

env.user = 'your_user'
env.host_string = 'your_host'

def add_teamcity_user():
    runcmd('adduser --system --shell /bin/bash --gecos \'TeamCity Build Control\' --group --disabled-password --home /opt/teamcity teamcity')

def download_teamcity():
    with cd('/opt/teamcity'):
        runcmd('wget http://download.jetbrains.com/teamcity/TeamCity-7.1.3.tar.gz')
        runcmd('tar -xzvf TeamCity-7.1.3.tar.gz')


def install_sun_java():
    runcmd('apt-get -y install software-properties-common')
    sudo('add-apt-repository -y ppa:webupd8team/java')
    sudo('apt-get update')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections')
    sudo('apt-get -q -y install oracle-java8-installer')


def start_on_startup():
    runcmd('chown -R www-data /opt/teamcity')
    upload_template('teamcity', '/etc/init.d/teamcity', use_sudo=True) # see template file
    runcmd('chmod 775 /etc/init.d/teamcity')
    runcmd('update-rc.d teamcity defaults')
    runcmd('/etc/init.d/teamcity start')

# Helpers
def runcmd(arg):
    if env.user != "root":
        sudo("%s" % arg, pty=True)
    else:
        run("%s" % arg, pty=True)

# Run entire setup
def setup_teamcity():
    install_sun_java()
    add_teamcity_user()
    download_teamcity()
    start_on_startup()

setup_teamcity()

# you should now be able to browse to 'http://localhost:8111/' to complete your teamcity installation...
# then I did this http://linuxconfig.org/linux-lvm-logical-volume-manager
"""
Thanks to

http://datagrams.blogspot.com/2013/02/install-teamcity-server-on-ubuntu-1204.html
http://askubuntu.com/questions/190582/installing-java-automatically-with-silent-option

"""
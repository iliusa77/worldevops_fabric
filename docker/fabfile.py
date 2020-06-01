from fabric.api import *
from unipath import Path
from fabtools.system import distrib_codename


class FabricException(Exception):
    pass

# the servers where the commands are executed
env.project = 'docker'

# the user to use for the remote commands

env.home = Path('/', 'home', env.user)
env.ssh = '/home/%s/.ssh' % env.user

env.local_root = Path(__file__).ancestor(1)
env.local_proj = Path(env.local_root, 'project')


@task
def setup():
    print(">>>>>>>>>   Setup docker phase 1. ")
    sudo('sudo apt-get update')
    sudo('sudo apt-get -y install apt-transport-https ca-certificates')
    sudo('sudo apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D')

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

    #On Debian Stretch/Sid
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

@task
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
    sudo('ufw allow ssh')
    sudo('echo \'DOCKER_OPTS="--dns 8.8.8.8 --dns 192.168.1.1"\' >> /etc/default/docker')
    with settings(abort_exception=FabricException):
        try:
            sudo('restart docker')
        except FabricException:
            pass
    sudo('systemctl enable docker')


@task
def test():
    sudo('echo \'DOCKER_OPTS="--dns 8.8.8.8 --dns 192.168.1.1"\' >> /etc/default/docker')


@task
def uninstall():
    sudo('apt-get -y purge docker-engine')
    sudo('apt-get -y autoremove')
    sudo('rm -rf /var/lib/docker')


def upgrade():
    sudo('apt-get -y upgrade docker-engine')

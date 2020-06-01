"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=ip=192.168.33.10 setup

"""
from fabric.api import *
import fabtools
from fabric.colors import green


def setup():
    sudo('wget http://repo.ajenti.org/debian/key -O- | sudo apt-key add -')
    sudo('echo "deb http://repo.ajenti.org/ng/debian main main ubuntu" | sudo tee -a /etc/apt/sources.list')
    sudo('apt-get update && apt-get -y dist-upgrade')
    sudo('apt-get -y install ajenti')
    fabtools.service.restart('ajenti')
    report()


def report():
    run("clear")
    print(green('Ajenti panel is installed'))
    print('You can access it on https://your_domain.com:8000 or https://droplet_ip:8000')
    print('Defult user is root and password admin')
from fabric.colors import green
from worldevops import *

zentyal_username = 'admin-zentyal'
zentyal_password = genpass()


def install_zentyal():
    sudo('echo "deb http://archive.zentyal.org/zentyal 4.2 main" >> /etc/apt/sources.list')
    sudo('apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 10E239FF')
    sudo('wget -q http://keys.zentyal.org/zentyal-4.2-archive.asc -O- | sudo apt-key add -')
    sudo('apt-get update && apt-get install -y zentyal zentyal-all && service zentyal start')


def add_zentyal_admin():
    sudo('adduser {username} --ingroup sudo --disabled-password --gecos "Admin Zentyal" '.format(username=zentyal_username))
    sudo('echo "{username}:{password}" | chpasswd'.format(username=zentyal_username,password=zentyal_password))


def report():
    run("clear")
    print(green("-------------------------------------------------------------------------------------------------------------------"))
    print(green("Congratulations, Zentyal Development Edition 4.2 has been successfully installed, visit https:your_domain_name:8443"))
    print(green("-------------------------------------------------------------------------------------------------------------------"))
    print('Admin username: {}'.format(zentyal_username))
    print('Admin password: {}'.format(zentyal_password))


def setup():
    install_zentyal()
    add_zentyal_admin()
    sudo('service zentyal restart')
    report()


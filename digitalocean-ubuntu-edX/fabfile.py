# for Ubuntu 12.04
'''
enter 192.168.33.10 demo.loc in /etc/hosts
how to run: fab -H demo.loc --user vagrant --password vagrant setup
'''

from fabric.api import *
from fabric.colors import green
import fabtools


def setup_system():
	sudo('apt-get update')
	fabtools.require.deb.packages([
        'build-essential', 'software-properties-common', 'software-properties-common',
        'curl', 'git-core', 'libxml2-dev', 'libxslt1-dev', 'libfreetype6-dev', 'python',
        'python-pip', 'python-apt', 'python-dev', 'libxmlsec1-dev', 'swig', 'libmysqlclient-dev'
    ])

def report():
    run("clear")
    print(green("----------------------------------------------------------------------------------------------"))
    print(green("edX-platform has been successfully installed"))
    print(green("for LMS visit http:demo.loc"))
    print(green("for Studio visit http:demo.loc:18010"))
    print(green("docroot is /edx/app/edxapp/edx-platform/lms/templates"))
    print(green("----------------------------------------------------------------------------------------------"))


def setup():
    setup_system()
    sudo('pip install --upgrade pip')
    sudo('pip install --upgrade virtualenv')
    with cd('/var/tmp'):
        sudo('git clone https://github.com/edx/configuration')
    with cd('/var/tmp/configuration'):
    	sudo('pip install -r requirements.txt')
        # sudo('pip install setuptools --upgrade')
    with cd('/var/tmp/configuration/playbooks'):
        sudo('ansible-playbook -c local ./edx_sandbox.yml -i "localhost,"')
	# report()


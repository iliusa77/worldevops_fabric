from fabric.api import *
from fabtools import require
import fabtools
import requests
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green


class FabricException(Exception):
    pass


env.user = 'vagrant'
env.password = 'vagrant'

env.hosts = [
    'demo.loc',
]
env.project = 'opencrx'
env.site = {
    'domain': "demo.loc"
}

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local_root = Path(__file__).ancestor(1)

env.projects_dir = Path('/', 'home', env.user, 'projects')


def install_jdk():
    print("______________________________________________________")
    print(green("JDK installation start"))
    with settings(abort_exception=FabricException):
        try:
            sudo("apt-get purge openjdk-7-jre gcj-4.7-base gcj-4.7-jre openjdk-6-jre-headless")
        except FabricException:
            pass
    sudo('apt-get update')
    sudo('add-apt-repository ppa:webupd8team/java')
    sudo('apt-get update')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections')
    sudo('apt-get -q -y install oracle-java7-installer')


def install_ant():
    print("______________________________________________________")
    print(green("Ant installation start"))
    if not fabtools.files.is_dir(env.project_dir):
        run('mkdir {}'.format(env.project_dir))
    with cd(env.project_dir):
        run('wget http://archive.apache.org/dist/ant/binaries/apache-ant-1.9.6-bin.tar.gz')
        run('tar xvfz apache-ant-1.9.6-bin.tar.gz')
        sudo('rm -rf {}'.format('/usr/local/apache-ant-1.9.6'))
        sudo('mv apache-ant-1.9.6 /usr/local/')
        run('echo "export ANT_HOME=/usr/local/apache-ant-1.9.6" >> ~/.profile')
        run('echo "export PATH=${PATH}:${ANT_HOME}/bin" >> ~/.profile ')
        run('source /home/{}/.profile'.format(env.user))
        run('rm apache-ant-1.9.6-bin.tar.gz')


def setup_autoinstall():
    print("______________________________________________________")
    print(green("Opencrx downloading and installation"))
    sudo("apt-get install unzip")
    tpl = 'install.xml'
    source = Path(env.local_root, 'app', 'config', tpl)
    sudo("rm -f %s" % tpl)
    upload_template(
        filename=source,
        destination=Path(env.project_dir),
        context={
            'project_dir': env.project_dir,
        }
    )
    with cd(env.project_dir):
        install_xml = Path(env.project_dir, 'install.xml')
        run(
            "curl -OL http://downloads.sourceforge.net/project/opencrx/opencrx/3.1.1/opencrxServer-3.1.1-installer.jre-1.7.jar")
        sudo("java -jar opencrxServer-3.1.1-installer.jre-1.7.jar -options {}".format(install_xml))


def start_server():
    print("______________________________________________________")
    print(green("Starting server"))

    with cd('/home/vagrant/opencrx/apache-tomee-webprofile-1.7.2/bin'):
        sudo('sudo ./opencrx.sh run')


def install_opencrx():
    print(green("Opencrx deployment"))
    install_jdk()
    install_ant()
    setup_autoinstall()
    installation_report()
    start_server()


def installation_report():
    print(green("____________________________________________________________________________________________"))
    print(green("ATTENTION!"))
    print("Before using server, read this message. Here you can find out usefull information about it.")
    print("host: http://demo.loc:8080/opencrx-core-CRX")
    print('\n')
    print("If you want to login as guest enter:")
    print("guest_login: guest")
    print("guest_pass:  guest")
    print('\n')
    print("If you want to login as admin-Standart enter:")
    print("admin_login: admin-Standart")
    print("admin_pass:  admin-Standart")
    print('\n')
    print("If you want to login as admin-Root enter:")
    print("admin_login: admin-Root")
    print("admin_pass:  admin-Root")
    print('\n')
    print("Please notice, that opencrx's default database is HSQLDB, but this CRM supports PostgreSQL, MySQL, DB/2, Oracle, and MS SQL Server."
          "In order to migrate use admin-Route account and guide https://sourceforge.net/p/opencrx/wiki/Admin31.DatabaseMigration/")


"""
Thanks to

http://askubuntu.com/questions/190582/installing-java-automatically-with-silent-option

"""

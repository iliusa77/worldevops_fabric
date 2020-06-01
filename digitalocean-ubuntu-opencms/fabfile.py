from fabric.api import *
from fabtools import require
import fabtools
import sys
from unipath import Path
from fabric.colors import green
from fabric.colors import red
from fabric.colors import blue
root = Path(__file__).ancestor(2)
sys.path.append(root)
from worldevops import *

class FabricException(Exception):
    pass

def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))

env.user = 'vagrant'
env.password = 'vagrant'

env.hosts = [
    'demo.loc',
]
env.project = 'opencms'
env.site = {
    'domain': "demo.loc"
}

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)

env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': 'test',#genpass(),
    'port': 3306,
    'root': 'test',#genpass()
}
env.admin = {
    'email': 'admin@%s.com' % env.project,
    'password': genpass()

}

env.conf = {'DB_PASSWD': 'rootpwd'}

def install_jdk():
    print("______________________________________________________")
    print(green("JDK installation start"))
    with settings(abort_exception=FabricException):
        try:
            sudo("apt-get purge openjdk-7-jre gcj-4.7-base gcj-4.7-jre openjdk-6-jre-headless", timeout=20)
        except FabricException:
            pass
    sudo('apt-get update')
    sudo('add-apt-repository -y ppa:webupd8team/java')
    sudo('apt-get update')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections')
    sudo('apt-get install -y oracle-java8-installer')
    run('echo "export JAVA_HOME=/usr/bin/java" >> ~/.profile')
    run('echo "export JRE_HOME=/usr/lib/jvm/java-8-oracle" >> ~/.profile')
    run('echo "export PATH=${PATH}:${JAVA_HOME}/bin" >> ~/.profile')
    run('echo "export PATH=${PATH}:${JRE_HOME}/bin" >> ~/.profile')

def install_tomcat():
    print("______________________________________________________")
    print(green("Tomcat installation start"))
    sudo('rm -rf /opt/tomcat')
    sudo('mkdir /opt/tomcat')
    sudo('chown {user}:{user} /opt/tomcat'.format(user=env.user))
    with cd('/opt/tomcat'):
        run('wget http://www-eu.apache.org/dist/tomcat/tomcat-8/v8.0.35/bin/apache-tomcat-8.0.35.tar.gz')
        run('tar xvf apache-tomcat-8*tar.gz -C /opt/tomcat --strip-components=1')
        run('rm apache-tomcat-8.0.35.tar.gz')
    run('echo "export CATALINA_HOME=/opt/tomcat" >> ~/.profile')
    run('echo "export CATALINA_BASE=/opt/tomcat" >> ~/.profile')
    run('echo "export PATH=${PATH}:${CATALINA_HOME}/bin" >> ~/.profile')
    run('echo "export PATH=${PATH}:${CATALINA_BASE}/bin" >> ~/.profile')


def deploy_opencms():
    print("______________________________________________________")
    print(green("Opencms downloading and installation"))
    sudo("apt-get install unzip")
    run("curl -OL http://www.opencms.org/downloads/opencms/opencms-10.0.0.zip")
    run('mv opencms-10.0.0.zip  /opt/tomcat/webapps ')
    with cd('/opt/tomcat/webapps'):
        run('unzip opencms-10.0.0.zip')
        run('rm opencms-10.0.0.zip')
        run('rm -rf ROOT')
        # run('mv opencms.war  ROOT.war ')
        # run('chmod 777 ROOT.war')
        run('chmod 777 opencms.war')
        run('$CATALINA_HOME/bin/startup.sh')

def setup_opencms():
    run('echo "export OPENCMS=/opt/tomcat/webapps/opencms" >> ~/.profile')
    run('echo "export CONFIG_FILE=/opt/tomcat/webapps/config" >> ~/.profile')
    run('echo "export PATH=${PATH}:${OPENCMS}/bin" >> ~/.profile')
    run('echo "export PATH=${PATH}:${CONFIG_FILE}/bin" >> ~/.profile')
    run('java -classpath "$OPENCMS/WEB-INF/lib/*:$OPENCMS/WEB-INF/classes:/opt/tomcat/lib/*"\
    org.opencms.setup.CmsAutoSetup -path $CONFIG_FILE')



def install_opencms():
    install_jdk()
    install_tomcat()
    install_mysql()
    deploy_opencms()
  #  setup_opencms()
  # print_report()

def print_report():
    print(green("Done"))
    run("clear")
    print(red("MYSQL database"))
    print (red("-----------------------------------"))
    print("host:  %s" % env.hosts)
    print("login:  %s" % env.db['user'])
    print("pass:  %s" % env.db['pass'])
    print(red(env.project," information"))
    print (red("-----------------------------------"))
    print("host:  %s" % env.site)


"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=ip=192.168.33.10,dbtype=mysql setup
             fab -H demo.loc --user vagrant --password vagrant --set=ip=192.168.33.10,dbtype=pgsql setup
             fab -H demo.loc --user vagrant --password vagrant --set=ip=192.168.33.10,dbtype=hs setup

"""

import sys
import fabtools
import requests
from fabric.api import *
from fabtools import require
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
from fabric.colors import red

root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *

class FabricException(Exception):
    pass

env.project = 'openfire'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.admin = {
    'email': 'admin@%s.com' % env.project,
    'password': genpass()

}

env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': '123123',
    'port': 3306,
    'root': '123123',
}

if env.dbtype == 'mysql':
    env.db['type'] = 'mysql'
    env.db['port'] = 3306
    env.db['driver'] = 'com.mysql.jdbc.Driver'

elif env.dbtype == 'pgsql':
    env.db['type'] = 'postgresql'
    env.db['port'] = 5432
    env.db['driver'] = 'org.postgresql.Driver'
else:
    env.db['type'] = 'hs'

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

def install_openfire():
    print("______________________________________________________")
    print(green("openfire downloading and installation"))
    run("curl -OL https://igniterealtime.org/downloadServlet?filename=openfire/openfire_4_0_2.tar.gz")
    run('tar xvfz openfire_4_0_2.tar.gz')
    run('rm openfire_4_0_2.tar.gz')
    if 'dbtype' in env:
        with cd('openfire/conf'):
            run('rm openfire.xml')
        if env.dbtype == 'pgsql':
            setup_pgsql()
        elif env.dbtype == 'mysql':
            setup_mysql()
    with cd('openfire/bin'):
        run('./openfire start')

def setup_pgsql():
    install_postgresql()
    source = Path(Path(__file__).ancestor(2), 'app', 'config', 'openfire.xml')
    print (red(source))
    destination = Path(env.project_dir + '/conf', 'openfire.xml')

    tpl = """
        <database>
      <defaultProvider>
      <driver>{driver}</driver>
      <serverURL>jdbc:{type}://{host}:{port}/{name}</serverURL>
      <username>{name}</username>
      <password>{pass}</password>
      <testSQL>select 1</testSQL>
      <testBeforeUse>false</testBeforeUse>
      <testAfterUse>false</testAfterUse>
      <minConnections>5</minConnections>
      <maxConnections>25</maxConnections>
      <connectionTimeout>1.0</connectionTimeout>
    </defaultProvider>
  </database>
                    """.format(**env.db)

    upload_template(
        filename=source,
        destination=destination,
        context={
            'tpl': tpl
        },
        use_sudo=True
    )

def setup_mysql():
    install_mysql()
    source = Path(Path(__file__).ancestor(2), 'app', 'config', 'openfire.xml')

    destination = Path(env.project_dir + '/conf', 'openfire.xml')

    tpl = """
        <database>
      <defaultProvider>
      <driver>{driver}</driver>
      <serverURL>jdbc:{type}://{host}:{port}/{name}?rewriteBatchedStatements=true</serverURL>
      <username>{name}</username>
      <password>{pass}</password>
      <testSQL>select 1</testSQL>
      <testBeforeUse>false</testBeforeUse>
      <testAfterUse>false</testAfterUse>
      <minConnections>5</minConnections>
      <maxConnections>25</maxConnections>
      <connectionTimeout>1.0</connectionTimeout>
    </defaultProvider>
  </database>
                    """.format(**env.db)

    upload_template(
        filename=source,
        destination=destination,
        context={
            'tpl': tpl
        },
        use_sudo=True
    )

def report():
    run("clear")
    print (red("-------------DB parametres--------------"))
    print("login:  %s" % env.db['user'])
    print("pass:  %s" % env.db['pass'])
    print("database name:  %s" % env.db['name'])
    print (red("-------------Openfire parametres--------------"))
    print(red("Please visit http://demo.loc:9090 to continue") )

def setup():
    install_jdk()
    install_openfire()
    report()
#
# -------------------------------------------------ATTENTION!-----------------------------------------------
# There are 3 different dotCMS configurations to install in this script. It's possible to install dotCMS with different '
# databases:H2(default database for evaluation and development), postgreSQL and MySQL.
# If you want to install dotCMS with H2DB enter in terminal:
# # fab setup -H 192.168.45.10 --user vagrant --password vagrant  --set=domain=192.168.45.10,dbtype
#
# If you want to install dotCMS with postgresql enter in terminal:
# # fab setup -H 192.168.45.10 --user vagrant --password vagrant  --set=domain=192.168.45.10,dbtype=pgsql
#
# If you want to install dotCMS with mysql enter in terminal:
# # fab setup -H 192.168.45.10 --user vagrant --password vagrant  --set=domain=192.168.45.10,dbtype=mysql


import sys
from unipath import Path
from fabric.colors import green
from fabric.colors import red
from fabric.contrib.files import upload_template

root = Path(__file__).ancestor(2)
sys.path.append(root)
from worldevops import *


class FabricException(Exception):
    pass

env.project = 'dotcms'
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
    env.db['type'] = 'h2db'


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

def install_dotcms():
    print("______________________________________________________")
    print(green("dotCMS downloading and installation"))
    run("curl -OL http://dotcms.com/physical_downloads/release_builds/dotcms_3.5.tar.gz")
    run('mkdir {}'.format(env.project_dir))
    run('mv dotcms_3.5.tar.gz  '+ env.project_dir)
    with cd(env.project_dir):
        run('tar xvfz dotcms_3.5.tar.gz')
        run('rm dotcms_3.5.tar.gz')
        run_app()
    if 'dbtype' in env:
        with cd(env.home + '/dotcms/dotserver/tomcat-8.0.18/webapps/ROOT/META-INF'):
            run('rm context.xml')
        if env.dbtype == 'pgsql':
            setup_postgresql()
        elif env.dbtype == 'mysql':
            setup_mysql()


def setup_postgresql():
    source = Path(Path(__file__).ancestor(1), 'app', 'config', 'context.xml')

    destination = Path(env.project_dir+'/dotserver/tomcat-8.0.18/webapps/ROOT/META-INF', 'context.xml')

    tpl = """
    <Resource name="jdbc/dotCMSPool" auth="Container"
        type="javax.sql.DataSource"
        driverClassName="{driver}"
        url="jdbc:{type}://{host}/dotcms"
        username="{user}" password="{pass}" maxTotal="60" maxIdle="10" maxWaitMillis="60000"
        removeAbandonedOnBorrow="true" removeAbandonedOnMaintenance="true" removeAbandonedTimeout="60" logAbandoned="true"
        timeBetweenEvictionRunsMillis="30000" validationQuery="SELECT 1" testOnBorrow="true" testWhileIdle="true" />
                """.format(**env.db)

    upload_template(
        filename=source,
        destination=destination,
        context={
            'tpl': tpl
        },
        use_sudo=True
    )
    install_postgresql()
    run_app()


def setup_mysql():
    source = Path(Path(__file__).ancestor(1), 'app', 'config', 'context.xml')

    destination = Path(env.project_dir + '/dotserver/tomcat-8.0.18/webapps/ROOT/META-INF', 'context.xml')

    tpl = """
    <Resource name="jdbc/dotCMSPool" auth="Container"
        type="javax.sql.DataSource"
        driverClassName="{driver}"
        url="jdbc:{type}://{host}/dotcms"
        username="{user}" password="{pass}" maxTotal="60" maxIdle="10" maxWaitMillis="60000"
        removeAbandonedOnBorrow="true" removeAbandonedOnMaintenance="true" removeAbandonedTimeout="60" logAbandoned="true"
        timeBetweenEvictionRunsMillis="30000" validationQuery="SELECT 1" testOnBorrow="true" testWhileIdle="true" />
                    """.format(**env.db)

    upload_template(
        filename=source,
        destination=destination,
        context={
            'tpl': tpl
        },
        use_sudo=True
    )
    install_mysql()
    run_app()

def run_app():
    run('echo "export DOTCMS_HOME=/home/vagrant/dotcms/dotserver/tomcat-8.0.18/webapps/ROOT" >> ~/.profile')
    run('echo "export DOTSERVER=dotcms" >> ~/.profile')
    run('echo "export CATALINA_PID=/tmp/dotcms.pid" >> ~/.profile')
    run('echo "export CATALINA_BASE=/home/vagrant/dotcms/dotserver/tomcat-8.0.18" >> ~/.profile')
    run('echo "export CATALINA_HOME=/home/vagrant/dotcms/dotserver/tomcat-8.0.18" >> ~/.profile')
    run('echo "export CATALINA_TMPDIR=/home/vagrant/dotcms/dotserver/tomcat-8.0.18/temp" >> ~/.profile')
    run('echo "export JAVA_OPTS=-Djava.awt.headless=true " >> ~/.profile')
    run('echo "export CLASSPATH=/home/vagrant/dotcms/dotserver/tomcat-8.0.18/bin/bootstrap.jar:/home/vagrant/dotcms/dotserver/tomcat-8.0.18/bin/tomcat-juli.jar " >> ~/.profile')
    run('echo "export PATH=${PATH}:${DOTCMS_HOME}/bin" >> ~/.profile')
    run('echo "export PATH=${PATH}:${DOTSERVER}/bin" >> ~/.profile')
    run('echo "export PATH=${PATH}:${CATALINA_PID}/bin" >> ~/.profile')
    run('echo "export PATH=${PATH}:${JAVA_OPTS}/bin" >> ~/.profile')
    run('echo "export PATH=${PATH}:${CATALINA_BASE}/bin" >> ~/.profile')
    run('echo "export PATH=${PATH}:${CATALINA_HOME}/bin" >> ~/.profile')
    run('echo "export PATH=${PATH}:${CATALINA_TMPDIR}/bin" >> ~/.profile')
    run('echo "export PATH=${PATH}:${CLASSPATH}/bin" >> ~/.profile')

    # start_script = '/bin/sh '+ env.project_dir + '/bin/startup.sh'
    # run(start_script)
    with cd(env.project_dir + '/bin'):
       sudo('./startup.sh',user=env.user)

def print_report():
    run("clear")
    print(red("Setup completed"))
    print (green("-----------DB Parametres-------------"))
    print("login:  %s" % env.db['user'])
    print("pass:  %s" % env.db['pass'])
    print("database name:  %s" % env.db['name'])
    print()
    print (red("-----------dotCMS Parametres-----------"))
    print("To create admin account visit - http://demo2.loc:8080/admin")
    print("Project available on url - http://demo2.loc:8080")
    print(red("In order to Log-in as admin, use :"))
    print("Email Address: admin@dotcms.com")
    print("Password : admin")



def setup():
    make_swap()
    common_setup()
    install_jdk()
    install_dotcms()
    print_report()

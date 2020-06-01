'''
how to run:  fab -H demo.loc --user vagrant --password vagrant setup
'''

from worldevops import *
from fabric.colors import red, green

env.project = 'openfire'

env.db = {
    'host': 'localhost',
    #'name': 'openfire',
    #'user': 'vagrant',
    #'pass': 'HXlpYcQV',
    'name': env.project,
    'user': env.user,
    'pass': genpass(),
    'port': 3306,
    #'root': 'aKRIrguS'
    'root': genpass()
}

def install_java8():
    sudo('add-apt-repository ppa:webupd8team/java -y')
    sudo('apt-get update')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections')
    sudo('apt-get install -y oracle-java8-installer')

def install_openfire():
    run('curl -OL https://www.igniterealtime.org/downloadServlet?filename=openfire/openfire_4.0.2_all.deb')
    sudo('dpkg -i openfire_4.0.2_all.deb')
    run('rm -f openfire_4.0.2_all.deb')
    #sudo('rm -f /etc/openfire/openfire.xml')
    #put('./config/openfire.xml', '/etc/openfire/', use_sudo=True)

#def import_db():
#    put('./config/openfire.sql', '/etc/openfire/', use_sudo=True)
#    sudo('mysql -u root -p%(root)s %(name)s < /etc/openfire/openfire.sql' % env.db)

def report():
    run("clear")
    print (red("-------------DB parametres--------------"))
    print("login:  %s" % env.db['user'])
    print("pass:  %s" % env.db['pass'])
    print("root pass:  %s" % env.db['root'])
    print("database name:  %s" % env.db['name'])
    print (green("-------------Openfire parametres--------------"))
    print(green("Please visit http://demo.loc:9090 to continue"))
    print(red("------------postinstall info-----------------------------------------------------------------------"))
    print(green("in step 3 for english Database URL: jdbc:mysql://localhost:3306/%s?rewriteBatchedStatements=true" % env.db['name']))
    print(red("---------------------------------------------------------------------------------------------------"))
    print(green("in step 3 for russian Database URL: jdbc:mysql://localhost:3306/%s?useUnicode=true&characterEncoding=UTF-8&characterSetResults=UTF-8" % env.db['name']))
    #print("login: admin")
    #print("pass: openfire")

def setup():
    install_java8()
    install_mysql()
    install_openfire()
   # import_db()
    report()
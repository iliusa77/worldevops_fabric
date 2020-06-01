from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import blue, green, red


class FabricException(Exception):
    pass


def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))


env.user = 'vagrant'
env.password = 'vagrant'

env.hosts = [
    'demo.loc'
]
env.project = 'vtigercrm'
env.hostname = "www.%s.com" % env.project
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
    'pass': genpass(),
    'port': 3306,
    'root': genpass()
}


def setup_apache():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    print(blue('Apache installed'))
    require.deb.packages(["php5", "php5-mysql", "php5-gd", "php5-imap", "php5-curl"])
    sudo("php5enmod imap")
    print(blue('PHP installed'))
    install_mysql()
    print(blue('MySQL installed'))
    install_project()
    config_apache()
    credentials()


def setup_nginx():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.nginx.server()
    print(blue('Nginx installed'))
    require.deb.packages(["php5-fpm", "php5-mysql", "php5-gd", "php5-imap", "php5-curl"])
    sudo("php5enmod imap")
    print(blue('PHP installed'))
    install_mysql()
    print(blue('MySQL installed'))
    install_project()
    config_nginx()
    credentials()


def install_mysql():
    require.mysql.server(password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        query = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (env.db['user'], env.db['pass'])
        fabtools.mysql.query(query=query, use_sudo=True)
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.database(env.db['name'], owner=env.db['user'])


def config_apache():
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()
    require.apache.site(
        '%s.com' % env.project,
        template_contents=config_tpl,
        port=80,
        hostname=env.site['domain'],
        document_root=env.project_dir
    )


def install_project():
    run("wget http://sourceforge.net/projects/vtigercrm/files/vtiger%20CRM%206.4.0/Core%20Product/vtigercrm6.4.0.tar.gz")
    run("tar zxvf vtigercrm6.4.0.tar.gz")
    with cd(env.home):
        sudo("chmod -R 0777 %s" % env.project)


def config_nginx():
    with open('./nginx/site.conf') as fn:
        config_tpl = fn.read()
    require.nginx.site(env.project,
                       template_contents=config_tpl,
                       port=80,
                       docroot=env.project_dir,
                       hostname=env.site['domain']
                       )
    require.nginx.enabled(env.project)


def credentials():
    print(green("Done"))
    run("clear")
    print(red("Database"))
    print (red("-----------------------------------"))
    print("login:  %s" % env.db['user'])
    print("pass:  %s" % env.db['pass'])
    print("database name:  %s" % env.db['name'])
    print (red("-----------------------------------"))
    print(blue("Please visit %s to continue installation" % env.site['domain']))
    print(blue("In installation you will see that need PHP 5.5.0 version, don`t worry it works on 5.5.9"))

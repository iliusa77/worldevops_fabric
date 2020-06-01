from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path


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
env.project = 'concrete5'
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


def install_mysql():
    require.mysql.server(password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        query = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (env.db['user'], env.db['pass'])
        fabtools.mysql.query(query=query, use_sudo=True)
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.database(env.db['name'], owner=env.db['user'])
    require.deb.package("php5-mysql")


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


def config_nginx():
    with open('./nginx/site.conf') as fn:
        config_tpl = fn.read()
    require.nginx.site(
        env.project,
        template_contents=config_tpl,
        port=80,
        docroot=env.project_dir,
        hostname=env.site['domain']
    )
    require.nginx.enabled(env.project)
    fabtools.require.service.restarted("nginx")


def install_project():
    sudo("apt-get install unzip")
    run("wget http://www.concrete5.org/download_file/-/view/58379/8497/ -O concrete5.zip")
    run("unzip concrete5.zip")
    run("mv concrete5*/ concrete5/")
    run("rm concrete5.zip")
    with cd(env.project_dir):
        sudo("chmod -R 0777 files/ config/ packages/ updates/")


def credentials():
    run("clear")
    print("Database")
    print ("-----------------------------------")
    print("login:  %s" % env.db['user'])
    print("pass:  %s" % env.db['pass'])
    print("database name:  %s" % env.db['name'])


def setup_apache():
    sudo("add-apt-repository -y ppa:ondrej/php5-5.6")
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    install_mysql()
    require.deb.packages(['php5', "php5-gd"])
    install_project()
    config_apache()
    credentials()


def setup_nginx():
    sudo("add-apt-repository -y ppa:ondrej/php5-5.6")
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.nginx.server()
    install_mysql()
    require.deb.packages(["php5-fpm", "php5-gd"])
    install_project()
    config_nginx()
    credentials()

from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path
from fabric.colors import red


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
env.project = 'piwik'
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


def install_project():
    require.deb.packages(["git", "unzip"])
    sudo("curl -sS https://getcomposer.org/installer | php")
    sudo("mv composer.phar /usr/local/bin/composer")
    run("wget http://builds.piwik.org/piwik.zip")
    run("unzip piwik.zip")
    with cd(env.project_dir):
        run("composer install")
    tmp_path = Path(env.project_dir, "tmp")
    conf_path = Path(env.project_dir, "config")
    sudo("chmod -R 0777 %s %s" % (tmp_path, conf_path))


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


def report():
    run("clear")
    print (red("-----------------------------------"))
    print(red("%s is successfully installed, visit http://%s to continue installation") % (env.project, env.site['domain']))
    print (red("-----------------------------------"))
    print ("Database Config :")
    print ("Db-Name: %s" % env.db['name'])
    print ("Db-User: %s" % env.db['user'])
    print ("Db-Password: %s" % env.db['pass'])


def setup_apache():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    install_mysql()
    require.deb.packages(['php5', 'php5-curl', "php5-gd"])
    install_project()
    config_apache()
    report()


def setup_nginx():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.nginx.server()
    install_mysql()
    require.deb.packages(["php5-cli", "php5-fpm", "php5-curl", "php5-gd"])
    install_project()
    config_nginx()
    report()

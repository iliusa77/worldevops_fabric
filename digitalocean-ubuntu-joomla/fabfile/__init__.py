"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10 setup_nginx

"""
from fabric.api import *
import fabtools
from unipath import Path
from fabric.colors import red
from worldevops import *

env.project = 'joomla'

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


def install_project():
    run("curl -sS https://getcomposer.org/installer | php")
    sudo("mv composer.phar /usr/local/bin/composer")
    fabtools.require.deb.package("git")
    run("composer global require joomlatools/console")
    sudo("ln -s %s/.config/composer/vendor/bin/joomla /usr/local/bin/joomla" % env.home)
    sudo("joomla site:create --www=%s --mysql-login=%s:%s --sample-data=default --disable-ssl --mysql-database=%s %s" % (env.home, env.db['user'], env.db['pass'], env.db['name'], env.project))


def config_apache():
    with open('../apache/site.conf') as fn:
        config_tpl = fn.read()
    fabtools.require.apache.site(
        env.domain,
        template_contents=config_tpl,
        port=80,
        domain=env.domain,
        docroot=env.project_dir
    )


def config_nginx():
    with open('../nginx/site.conf') as fn:
        config_tpl = fn.read()
    fabtools.require.nginx.site(
        env.project,
        template_contents=config_tpl,
        port=80,
        docroot=env.project_dir,
        hostname=env.domain
    )


def report():
    run("clear")
    print (red("-----------------------------------"))
    print(red("Congratulations, Joomla has been successfully installed, visit http://%s") % env.domain)
    print(red("To administration site, visit http://%s/administrator") % env.domain)
    print(red("lodin - admin"))
    print(red("password - admin"))


def setup_apache():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    sudo("a2enmod rewrite")
    sudo("service apache2 restart")
    fabtools.require.deb.packages(['php5', "unzip", "php5-mysql"])
    install_mysql()
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root', mysql_password=env.db['root'])
    install_project()
    config_apache()
    report()


def setup_nginx():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.nginx.server()
    fabtools.require.deb.packages(['php5-cli', "php5-fpm", "unzip", "php5-mysql"])
    install_mysql()
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root', mysql_password=env.db['root'])
    install_project()
    config_nginx()
    report()

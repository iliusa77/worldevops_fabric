"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10 setup

"""
from fabtools import require
from unipath import Path
import sys
from fabric.colors import red
from fabric.contrib.files import upload_template
root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *

env.project = 'zurmo'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))

env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': genpass(),
    'port': 3306,
    'root': genpass()
}


def install_mysql():
    with settings(abort_exception=FabricException):
        try:
            fabtools.require.mysql.server(password=env.db['root'])
        except FabricException:
            sudo('apt-get -f -y install')

    fabtools.require.deb.packages(['libmysqlclient-dev'])


def install_project():
    run("wget http://build.zurmo.com/downloads/zurmo-stable-3.1.5.a5a46793e4a5.tar.gz")
    run("tar xopf zurmo-stable-3.1.5.a5a46793e4a5.tar.gz")
    sudo("chown -R www-data:www-data %s" % env.project_dir)


def config_apache():
    with open(env.local+'/apache/site.conf') as fn:
        config_tpl = fn.read()

    fabtools.require.apache.site(
        '%s.com' % env.project,
        template_contents=config_tpl,
        port=80,
        domain=env.domain,
        docroot=env.project_dir
    )


def report():
    run("clear")
    print (red("-----------------------------------"))
    print ("DB-root-password: %s" % env.db['root'])
    print(red("To continue installation please visit %s") % env.domain)


def setup():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.deb.package(["apache2",
                                  "php5",
                                  "php5-memcache",
                                  "php5-curl",
                                  "php-apc",
                                  "php-soap",
                                  "php5-imap",
                                  "memcached",
                                  "php5-gd",
                                  "php-pear",
                                  "php5-ldap",
                                  "php5-mcrypt",
                                  "php5-mysql"])
    sudo("php5enmod mcrypt")
    sudo("php5enmod imap")
    install_mysql()
    install_project()
    config_apache()
    report()

"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10 setup

"""
from fabtools import require
from unipath import Path
from fabric.colors import red
from fabric.contrib.files import upload_template
import sys
root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *

env.project = 'osticket'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))

env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': "123123",
    'port': 3306,
    'root': "123123"
}


def install_project():
    run("git clone https://github.com/osTicket/osTicket %s" % env.project)
    with cd(env.project_dir):
        run("git checkout tags/v1.9.12")
        run("cp include/ost-sampleconfig.php include/ost-config.php")
        run("chmod 0666 include/ost-config.php")


def config_apache():
    with open('./apache/site.conf') as fn:
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
    print(red("Please visit %s to continue") % env.domain)


def setup():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    fabtools.require.deb.packages(['php5', "php5-mysql", "php5-mcrypt", "php5-gd", "php5-intl", "php5-apcu", "php5-imap", "git"])
    sudo("php5enmod imap")
    fabtools.service.reload("apache2")
    install_mysql()
    install_project()
    config_apache()
    report()
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

env.project = 'simpleinvoices'

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


def install_project():
    run("wget http://simpleinvoices.googlecode.com/files/simpleinvoices.2010.2.update-1.zip")
    run("unzip simpleinvoices.2010.2.update-1.zip")
    with cd(env.project_dir):
        source = Path(env.local, "simpleinvoices", "config.ini")
        destination = Path(env.project_dir, "config", "config.ini")
        upload_template(
            filename=source,
            destination=destination,
            context={
                'host': env.db['host'],
                'user': env.db['user'],
                'pass': env.db['pass'],
                'name': env.db['name'],
            }
        )
        run("chmod -Rv 777 tmp*")


def config_apache():
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()

    fabtools.require.apache.site(
        '%s.com' % env.project,
        template_contents=config_tpl,
        port=80,
        domain=env.domain,
        docroot=env.project_dir,
        project=env.project,
    )


def report():
    run("clear")
    print (red("-----------------------------------"))
    print(red("simpleinvoices was installed please visit %s") % env.domain)


def setup():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    fabtools.require.apache.enable_module('rewrite')
    fabtools.service.reload('apache2')
    fabtools.require.deb.packages(['php5', "php5-mysql", "php5-gd", "php5-xsl", "unzip"])
    install_mysql()
    install_project()
    config_apache()
    report()

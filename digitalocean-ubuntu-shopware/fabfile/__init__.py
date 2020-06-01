"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10 setup_apache

"""
from fabric.contrib.files import upload_template
from unipath import Path
from fabric.colors import red
import fabtools
import sys
root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *

env.project = 'shopware'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)

env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': '123123',
    'port': 3306,
    'root': '123123',
    'type': 'mysql',
    'driver': 'pdo_mysql'

}


def install_project():
    run("git clone https://github.com/shopware/shopware.git shopware")
    with cd(env.project_dir):
        run("chmod -R 755 var/ web/ files/ media/ engine/Shopware/Plugins/Community/")
        conf_file = Path(Path(__file__).ancestor(2), 'shopware', 'build.properties')
        destination = Path(env.project_dir, "build", "build.properties")
        upload_template(
            filename=conf_file,
            destination=destination,
            context={
                'user': env.db['user'],
                'pass': env.db['pass'],
                'name': env.db['name'],
                'host': env.db['host'],
                'port': env.db['port'],
                'app_host': env.domain,
                'app_path': env.project_dir
            }
        )
        with cd(env.project_dir + "/build"):
            run("ant build-unit")
        run("chmod -R 0777 var/cache/ var/log/")
        run("chmod 755 config.php")


def config_apache():
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()
    fabtools.require.apache.site(
        env.domain,
        template_contents=config_tpl,
        port=80,
        domain=env.domain,
        docroot=env.project_dir
    )


def report():
    run("clear")
    print (red("-----------------------------------"))
    print(red("Visit %s/backend to continue") % env.domain)
    print(red("lodin - demo"))
    print(red("password - demo"))


def setup_apache():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    sudo("a2enmod rewrite")
    fabtools.require.deb.packages(
        ['php5', "php5-gd", "php5-curl", "php5-mysql", "git", "ant"]
    )
    install_mysql()
    install_project()
    config_apache()
    report()


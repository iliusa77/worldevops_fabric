"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10,project={project_name} setup

"""
from fabtools import require
from unipath import Path
from fabric.colors import red
from fabric.contrib.files import upload_template
import sys
root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *

env.project = 'cakephp'

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
    run("git clone -b 2.x git://github.com/cakephp/cakephp.git %s" % env.project)
    with cd(env.project_dir):
        run("chmod -R 777 app/tmp/")
        source = Path(env.local, "cakephp", "database.php")
        destination = Path(env.project_dir, "app", "Config", "database.php")
        upload_template(
            filename=source,
            destination=destination,
            context={
                'user': env.db['user'],
                'password': env.db['pass'],
                'name': env.db['name'],
            }
        )
        source = Path(env.local, "cakephp", "core.php")
        destination = Path(env.project_dir, "app", "Config", "core.php")
        upload_template(
            filename=source,
            destination=destination,
        )
        sudo("curl -sS https://getcomposer.org/installer | php")
        sudo("mv composer.phar /usr/local/bin/composer")
        run("composer require cakephp/debug_kit \"^2.2.0\"")
        run("mv Plugin/DebugKit/ app/Plugin/")


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
    print(red("CakePHP framework was installed please visit %s") % env.domain)


def setup():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    fabtools.require.apache.enable_module('rewrite')
    fabtools.service.reload('apache2')
    fabtools.require.deb.packages(['php5', "php5-mysql", "php5-mcrypt", "git"])
    install_mysql()
    install_project()
    config_apache()
    report()

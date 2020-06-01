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

env.project = 'wekan'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))


def install_mongodb():
    sudo("apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927")
    sudo("echo \"deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.2 multiverse\" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list")
    sudo("apt-get update")
    fabtools.require.deb.package("mongodb-org")


def install_project():
    run("mkdir -p %s/wekan" % env.home)
    run("curl -LOk https://github.com/wekan/wekan/releases/download/v0.10.1/wekan-0.10.1.tar.gz")
    run("tar xzvf wekan-0.10.1.tar.gz -C %s/wekan" % env.home)
    with cd(env.project_dir+"/bundle/programs/server"):
        run("npm install")


def install_forever_service():
    sudo("npm install forever -g")
    source = Path(env.local, 'wekan', 'wekan.conf')
    target = Path("/", "etc", "init", "wekan.conf")
    print (red(env.home))
    print (red(env.project_dir))
    upload_template(
        filename=source,
        destination=target,
        context={
            'home_path': env.home,
            'project_dir': env.project_dir,
        },
        use_sudo=True)
    sudo("chown root:root %s" % target)
    sudo("chmod 644 %s" % target)
    sudo("service wekan start")


def install_nginx():
    fabtools.require.nginx.server()
    fabtools.require.nginx.disable('default')
    with open(env.local + '/nginx/site.conf') as fn:
        config_tpl = fn.read()
    fabtools.require.nginx.site('default',
                                template_contents=config_tpl,
                                port=80,
                                domain=env.domain,
                                )


def report():
    run("clear")
    print (red("-----------------------------------"))
    print(red("Plese visit http://%s and register a new user") % env.domain)


def setup():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.deb.packages(["software-properties-common", "libssl-dev", "curl", "build-essential"])
    fabtools.nodejs.install_from_source(version="0.10.40")
    install_mongodb()
    install_project()
    install_forever_service()
    install_nginx()
    report()



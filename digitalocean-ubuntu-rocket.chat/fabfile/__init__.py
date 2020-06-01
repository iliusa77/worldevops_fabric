"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10 setup

"""
from fabtools import require
from unipath import Path
from fabric.colors import red
import sys
root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *

env.project = 'rocketchat'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))


def setup_nginx():
    fabtools.require.nginx.server()
    cert_path = Path("/", "etc", "nginx", "ssl")
    sudo("mkdir %s" % cert_path)
    with cd(cert_path):
        sudo(
            "openssl req -x509 -nodes -days 365 -newkey rsa:2048 -subj \"/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.%s\" -keyout %s/%s.key -out %s/%s.crt" % (
            env.domain, cert_path, env.project, cert_path, env.project))
    fabtools.require.nginx.disable('default')
    with open(env.local+'/nginx/site.conf') as fn:
        config_tpl = fn.read()
    fabtools.require.nginx.site('default',
                       template_contents=config_tpl,
                       port=443,
                       domain=env.domain,
                       project=env.project,
                       certificates_path=Path("/", "etc", "nginx", "ssl", env.project)
                       )


def report():
    run("clear")
    print (red("-----------------------------------"))
    print(red("Plese visit https://%s and register a new user") % env.domain)


def setup():
    sudo("apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927")
    sudo("echo \"deb http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.2 multiverse\" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list")
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.deb.packages(['mongodb-org', "npm", "curl", "graphicsmagick"])
    sudo("npm install -g n")
    sudo("n 0.10.40")
    run("curl -L https://rocket.chat/releases/latest/download -o rocket.chat.tgz")
    run("tar zxvf rocket.chat.tgz")
    run("mv bundle Rocket.Chat")
    with cd("Rocket.Chat"):
        with cd("programs/server"):
            run("npm install")
        run("export ROOT_URL=https://demo.loc/")
        run("export MONGO_URL=mongodb://localhost:27017/rocketchat")
        run("export PORT=3000")
    sudo("npm install -g forever")
    sudo("npm install -g forever-service")
    with cd("Rocket.Chat"):
        sudo("forever-service install -s main.js -e \"ROOT_URL=https://demo.loc/ MONGO_URL=mongodb://localhost:27017/rocketchat PORT=3000\" rocketchat")
    sudo("start rocketchat")
    setup_nginx()
    report()


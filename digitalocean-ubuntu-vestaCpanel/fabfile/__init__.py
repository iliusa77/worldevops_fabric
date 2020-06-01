"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10 setup

"""
from fabtools import require
from unipath import Path
import sys
from fabric.colors import red
root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *

env.project = 'vesta'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))
env.admin_pass = genpass()


def report():
    run("clear")
    print (red("-----------------------------------"))
    print("Vesta Control Panel was installed please visit https://%s:8083" % env.domain)
    print ("Username - admin")
    print ("Password - %s" % env.admin_pass)
    print (red("-----------------------------------"))


def setup():
    sudo("apt-get update && apt-get -y dist-upgrade")
    run("curl -O http://vestacp.com/pub/vst-install.sh")
    sudo("bash vst-install.sh -s %s -e admin@%s -p %s -y no  -f" % (env.domain, env.domain, env.admin_pass))
    report()

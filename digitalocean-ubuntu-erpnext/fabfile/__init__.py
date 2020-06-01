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

env.project = 'erpnext'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))


def setup():
    run("wget https://raw.githubusercontent.com/frappe/bench/master/install_scripts/setup_frappe.sh")
    sudo("bash setup_frappe.sh --setup-production")
    report()


def report():
    with cd(env.home):
        run("clear")
        print (red("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"))
        run("cat frappe_passwords.txt")
        print("ErpNext was installed please visit %s" % env.domain)
        print (red("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"))
        sudo("rm frappe_passwords.txt frappe_passwords.sh")


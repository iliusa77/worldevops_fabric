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

env.project = 'etherpad'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))


def report():
    run("clear")
    print (red("-----------------------------------"))
    print(red("Etherpad was installed please visit %s") % env.domain)


def config_apache():
    fabtools.require.apache.enable_module("proxy")
    fabtools.require.apache.enable_module("proxy_http")
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()
    fabtools.require.apache.site(
        env.domain,
        template_contents=config_tpl,
        port=80,
        hostname=env.domain,
        document_root=env.project_dir
    )


def setup():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    fabtools.require.deb.packages([
        "gzip",
        "git",
        "curl",
        "python",
        "libssl-dev",
        "pkg-config",
        "build-essential",
        "supervisor"
    ])
    run("curl -sL https://deb.nodesource.com/setup | sudo bash -")
    fabtools.require.deb.package("nodejs")
    fabtools.git.clone(
        'git://github.com/ether/etherpad-lite.git',
        user=env.user
    )
    source = Path(env.local, "etc", 'supervisor', 'etherpad.conf')
    destination = Path('/', 'etc', 'supervisor', 'conf.d', 'etherpad.conf')
    upload_template(
        filename=source,
        destination=destination,
        use_sudo=True
    )
    fabtools.service.restart('supervisor')
    config_apache()
    report()


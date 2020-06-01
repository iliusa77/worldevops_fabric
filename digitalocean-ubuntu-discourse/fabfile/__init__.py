"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10,admin_email=admin@demo.com,smtp_port=587,smtp_domain=smtp.gmail.com,smtp_user=postmaster@demo.loc,smtp_pass=123123 setup

"""
from fabtools import require
from unipath import Path
from fabric.colors import red
from fabric.contrib.files import upload_template
import sys
root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *

env.project = 'discourse'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))


def report():
    run("clear")
    print (red("-----------------------------------"))
    print(red("Please visit %s to continue") % env.domain)


def setup():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.deb.package("git")
    sudo("wget -qO- https://get.docker.io/ | sh")
    sudo("usermod -aG docker %s" % env.user)
    sudo("mkdir /var/discourse")
    sudo("git clone https://github.com/discourse/discourse_docker.git /var/discourse")
    with cd("/var/discourse"):
        source_file = Path(env.local, "config", "app.yml")
        destination = Path("/var/discourse", "containers", "app.yml")
        upload_template(
            filename=source_file,
            destination=destination,
            context={
                'host': env.domain,
                'email': env.admin_email,
                'port': env.smtp_port,
                'smtp_domain': env.smtp_domain,
                'smtp_user': env.smtp_user,
                'smtp_pass': env.smtp_pass,
            },
            use_sudo=True,
        )
        source_file = Path(env.local, "config", "docker")
        destination = Path("/", "etc", "default", "docker")
        upload_template(
            filename=source_file,
            destination=destination,
            use_sudo=True
        )
        sudo("service docker restart")
        sudo("./launcher bootstrap app")
        sudo("./launcher start app")
    report()

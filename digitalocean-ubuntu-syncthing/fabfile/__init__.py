# for Ubuntu 14.04
'''
enter 192.168.33.10 demo.loc in /etc/hosts
how to run: fab -H demo.loc --user vagrant --password vagrant setup

'''

from fabric.api import *
from fabric.colors import green
import fabtools
from unipath import Path

env.project = 'syncthing'
env.home = Path('/home/', env.user)
home_project = Path(env.home, env.project)
public_ip = '0.0.0.0'
public_port = '8384'

def setup_syncthing():
	sudo('curl -s https://syncthing.net/release-key.txt | \
  sudo apt-key add - ')
	sudo('echo "deb http://apt.syncthing.net/ syncthing release" | \
  sudo tee /etc/apt/sources.list.d/syncthing.list ')
	sudo('apt-get update && apt-get install -y syncthing supervisor')

def start_syncthing():
	run('mkdir {}'.format(home_project))
	fabtools.require.file('{}/run.sh'.format(env.home), """\
#!/bin/sh
/usr/bin/syncthing -no-browser -gui-address="http://{0}:{1}" -home={2}""".format(public_ip, public_port, home_project))
	run('chmod u+x {}/run.sh'.format(env.home))
	fabtools.require.file('/etc/supervisor/conf.d/syncthing.conf', """\
[program:syncthing]
process_name=syncthing
directory=/usr/bin/
user={0}
numprocs=1
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/supervisor/syncthing.log
command={1}/run.sh
""".format(env.user, env.home), use_sudo=True)
	sudo('supervisorctl reload')

def report():
    run("clear")
    print(green(
        "-------------------------------------------------------------------------"))
    print(green("Syncthing been successfully installed, visit http://demo.loc:8384"))
    print(green("-----------------------------------------------------------------"))

def setup():
	setup_syncthing()
	start_syncthing()
	report()

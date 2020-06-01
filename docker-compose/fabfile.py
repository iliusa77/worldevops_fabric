#for Ubuntu 14.04
'''
run: fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc setup

'''

from fabric.api import *
from unipath import Path
from fabric.colors import green, red
from fabtools import require
import fabtools
from fabric.contrib.files import upload_template
from jinja2 import *


class FabricException(Exception):
    pass

# the servers where the commands are executed
env.project = 'docker-compose'
env.sub1 = 'ma.{}'.format(env.domain)
env.sub2 = 'crm.{}'.format(env.domain)
env.sub3 = 'mail.{}'.format(env.domain)

# the user to use for the remote commands

env.home = Path('/', 'home', env.user)
env.ssh = '/home/%s/.ssh' % env.user

env.local_root = Path(__file__).ancestor(1)
env.local_proj = Path(env.home, env.project)
env.local_wordpress = Path(env.home, env.project, 'wordpress')
env.local_mautic = Path(env.home, env.project, 'mautic')
env.local_suitecrm = Path(env.home, env.project, 'suitecrm')
env.local_mailserver = Path('/', 'freeposte')

def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))

wppass = 'wordpress'
crmpass = genpass()
mapass = genpass()
mailpass = genpass()

#Change to client company details
env.reqdata = {
    'country': 'GB',
    'state': 'Nottingham',
    'locality': 'Nottinghamshire',
    'organization': '{}'.format(env.domain),
    'organizationalunit': 'IT',
    'email': 'administrator@{}'.format(env.domain),
    'commonname': env.domain
}

def common_setup():
    sudo('apt-get update')
    sudo('mkdir {}'.format(env.local_proj))
    sudo('echo "127.0.0.1 {0} {1} {2} {3}" >> /etc/hosts'.format(env.domain, env.sub1, env.sub2, env.sub3))

def install_compose():
    sudo('apt-get -y install python-pip')
    sudo('pip install docker-compose')

def upgrade_compose():
    sudo('docker-compose migrate-to-labels')

def uninstall_compose():
    sudo('pip uninstall docker-compose')

def install_nginx():
    fabtools.require.nginx.server()
    fabtools.require.nginx.disabled('default')
    with open('configs/nginx/wordpress.conf') as fn:
        config_tpl = fn.read()
    require.nginx.site(env.domain,
                       template_contents=config_tpl,
                       domain=env.domain,
                       )
    require.nginx.enabled(env.domain)
    with open('configs/nginx/mautic.conf') as fn:
        config_tpl = fn.read()
    require.nginx.site(env.sub1,
                       template_contents=config_tpl,
                       sub1=env.sub1,
                       )
    require.nginx.enabled(env.sub1)
    with open('configs/nginx/suitecrm.conf') as fn:
        config_tpl = fn.read()
    require.nginx.site(env.sub2,
                       template_contents=config_tpl,
                       sub2=env.sub2,
                       )
    require.nginx.enabled(env.sub2)
    with open('configs/nginx/mailserver.conf') as fn:
        config_tpl = fn.read()
    require.nginx.site(env.sub3,
                       template_contents=config_tpl,
                       sub3=env.sub3,
                       )
    require.nginx.enabled(env.sub3)
    sudo('service nginx restart')


#wordpress 4.6.1
def install_wordpress():
    sudo('mkdir {}'.format(env.local_wordpress))
    with cd(env.local_wordpress):
        tpldir = str(Path('configs', 'wordpress'))
        target = str(Path('./'))
        context = {
          'wppass': wppass,
        }
        upload_template(
          filename="docker-compose.yml",
          destination=target,
          context=context,
          use_jinja=True,
          template_dir=tpldir,
          use_sudo=True
        )
        sudo('docker-compose up -d')
    print(green("--------------------------------------------------------------------------------------"))
    print(green("Wordpress was successful installed, to continue visit http://{}".format(env.domain)))
    print(green("--------------------------------------------------------------------------------------"))
    print(green("dbuser: wordpress, dbpass:{}".format(wppass)))
    print(green("--------------------------------------------------------------------------------------"))


def start_wordpress():
    with cd(env.local_wordpress):
        sudo('docker-compose start')

def stop_wordpress():
    with cd(env.local_wordpress):
        sudo('docker-compose stop')

def remove_wordpress():
    with cd(env.local_wordpress):
        sudo('docker-compose down')
    with cd(env.home):
        sudo('rm -r {}'.format(env.local_wordpress))


#mautic 2.2.1
#for version 1.2.4 switch to "image: mautic/mautic" in docker-compose
def install_mautic():
    sudo('mkdir {}'.format(env.local_mautic))
    with cd(env.local_mautic):
        tpldir = str(Path('configs', 'mautic'))
        target = str(Path('./'))
        context = {
          'mapass': mapass,
        }
        upload_template(
          filename="docker-compose.yml",
          destination=target,
          context=context,
          use_jinja=True,
          template_dir=tpldir,
          use_sudo=True
        )
        sudo('docker-compose up -d')
    print(green("--------------------------------------------------------------------------------------"))
    print(green("Mautic was successful installed, to continue visit http://{}".format(env.sub1)))
    print(green("--------------------------------------------------------------------------------------"))
    print(green("Mysql info:"))
    print(green("dbuser: root"))
    print(green("dbroot_password: {}".format(mapass)))


def start_mautic():
    with cd(env.local_mautic):
        sudo('docker-compose start')

def stop_mautic():
    with cd(env.local_mautic):
        sudo('docker-compose stop')

def remove_mautic():
    with cd(env.local_mautic):
        sudo('docker-compose down')
    with cd(env.home):
        sudo('rm -r {}'.format(env.local_mautic))

#suitecrm 7.2.2
def install_suitecrm():
    #with cd(env.local_proj): #for version 7.2.2
    #    sudo('git clone https://github.com/thibremy/docker-suitecrm.git') #for version 7.2.2
    #    sudo('mv {0}/docker-suitecrm {0}/suitecrm'.format(env.local_proj)) #for version 7.2.2
    #for version 7.2.2 switch to "build: 7.2.2" in docker-compose
    sudo('mkdir {}'.format(env.local_suitecrm))
    with cd('{0}/suitecrm'.format(env.local_proj)):
        tpldir = str(Path('configs', 'suitecrm'))
        target = str(Path('./'))
        context = {
          'sub2': env.sub2,
          'crmpass': crmpass,

        }
        upload_template(
          filename="docker-compose.yml",
          destination=target,
          context=context,
          use_jinja=True,
          template_dir=tpldir,
          use_sudo=True
        )
        sudo('docker-compose up -d')
    print(green("--------------------------------------------------------------------------------------"))
    print(green("Suitecrm was successful installed, to continue visit http://{}".format(env.sub2)))
    print(green("--------------------------------------------------------------------------------------"))
    print(green("Mysql info:"))
    print(green("dbhost: mysql"))
    print(green("dbname: suitecrm"))
    print(green("dbroot_password: {}".format(crmpass)))
    print(green("db_user: suitecrm"))
    print(green("db_password: {}".format(crmpass)))
    
def start_suitecrm():
    with cd(env.local_suitecrm):
        sudo('docker-compose start')

def stop_suitecrm():
    with cd(env.local_suitecrm):
        sudo('docker-compose stop')

def remove_suitecrm():
    with cd(env.local_suitecrm):
        sudo('docker-compose down')
    with cd(env.home):
        sudo('rm -r {}'.format(env.local_suitecrm))

#Mailserver (Freeposte.io)
def install_mailserver():
    sudo('mkdir {}'.format(env.local_mailserver))
    with cd(env.local_proj):
        sudo('ln -s {0} mailserver'.format(env.local_mailserver))
    with cd(env.local_mailserver):
    #    sudo('wget https://raw.githubusercontent.com/kaiyou/freeposte.io/master/docker-compose.yml')
    #    sudo('wget https://raw.githubusercontent.com/kaiyou/freeposte.io/master/.env')
        source = Path('configs', 'mailserver', 'docker-compose.yml')
        put(local_path=source, remote_path=env.local_mailserver, use_sudo=True)
        tpldir = str(Path('configs', 'mailserver'))
        target = str(Path('/', 'freeposte'))
        context = {
          'domain': env.domain,
          'hostname': env.sub3,

        }
        upload_template(
          filename=".env",
          destination=target,
          context=context,
          use_jinja=True,
          template_dir=tpldir,
          use_sudo=True
        )
        sudo('docker-compose up -d')
        sudo('docker-compose stop')
    with cd('{}/certs'.format(env.local_mailserver)):
        sudo('openssl req -new -x509 -days 3650 -nodes -out cert.pem -keyout key.pem \
        -subj "/C=%(country)s/ST=%(state)s/L=%(locality)s/O=%(organization)s/OU=%(organizationalunit)s/CN=%(commonname)s/emailAddress=%(email)s"' % env.reqdata)
        sudo('chmod o= *.pem')
        sudo('docker-compose start')
        sudo('docker-compose stop')
    with cd(env.local_mailserver):
        sudo('docker-compose run --rm admin python manage.py admin admin {0} {1}'.format(env.domain, mailpass))
        sudo('docker-compose start')
    print(green("------------------------------------------------------------------------------"))
    print(green("Mailserver was successful installed, for administration visit http://{}/admin".format(env.sub3)))
    print(green("username: admin@{0}, password: {1}".format(env.domain, mailpass)))
    print(green("------------------------------------------------------------------------------"))
    print(green("Roundcube url: http://{}".format(env.sub3)))
    print(green("------------------------------------------------------------------------------"))    

def start_mailserver():
    with cd(env.local_mailserver):
        sudo('docker-compose start')

def stop_mailserver():
    with cd(env.local_mailserver):
        sudo('docker-compose stop')

def remove_mailserver():
    with cd(env.local_mailserver):
        sudo('docker-compose down')

def remove_mailserver_force():
    with cd(env.local_mailserver):
        sudo('docker-compose down')
    with cd('/'):
        sudo('rm -r {}'.format(env.local_mailserver))

def common_report():
    print(green("--------------------------------------------------------------------------------------"))
    print(green("Wordpress was successful installed, to continue visit http://{}".format(env.domain)))
    print(green("--------------------------------------------------------------------------------------"))
    print(green("dbuser: wordpress, dbpass:{}".format(wppass)))
    print(green("--------------------------------------------------------------------------------------"))
    print(red("----------------------------------------------------------------------------------------"))
    print(green("--------------------------------------------------------------------------------------"))
    print(green("Mautic was successful installed, to continue visit http://{}".format(env.sub1)))
    print(green("--------------------------------------------------------------------------------------"))
    print(green("Mysql info:"))
    print(green("dbuser: root"))
    print(green("dbroot_password: {}".format(mapass)))
    print(red("----------------------------------------------------------------------------------------"))
    print(green("--------------------------------------------------------------------------------------"))
    print(green("Suitecrm was successful installed, to continue visit http://{}".format(env.sub2)))
    print(green("--------------------------------------------------------------------------------------"))
    print(green("Mysql info:"))
    print(green("dbhost: mysql"))
    print(green("dbname: suitecrm"))
    print(green("dbroot_password: {}".format(crmpass)))
    print(green("db_user: suitecrm"))
    print(green("db_password: {}".format(crmpass)))
    print(red("----------------------------------------------------------------------------------------"))
    print(green("------------------------------------------------------------------------------"))
    print(green("Mailserver was successful installed, for administration visit http://{}/admin".format(env.sub3)))
    print(green("username: admin@{0}, password: {1}".format(env.domain, mailpass)))
    print(green("------------------------------------------------------------------------------"))
    print(green("Roundcube url: http://{}".format(env.sub3)))
    print(green("------------------------------------------------------------------------------"))


def setup():
    common_setup()
    install_compose()
    install_nginx()
    install_wordpress()
    install_mautic()
    install_suitecrm()
    install_mailserver()
    common_report()

def start_all():
    start_wordpress()
    start_mautic()
    start_suitecrm()
    start_mailserver()

def stop_all():
    stop_wordpress()
    stop_mautic()
    stop_suitecrm()
    stop_mailserver()

def remove_all():
    remove_wordpress()
    remove_mautic()
    remove_suitecrm()
    remove_mailserver()



    

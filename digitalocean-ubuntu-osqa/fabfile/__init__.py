"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10,project={project_name} setup

"""
import sys
import fabtools
import requests
from fabric.api import *
from fabtools import require
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
from fabric.colors import red

root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *

class FabricException(Exception):
    pass

env.project = 'osqa'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))
env.admin = {
    'email': 'admin@%s.com' % env.project,
    'password': genpass()

}

env.db = {
    'driver': 'django.db.backends.mysql',
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': genpass(),
    'port': 3306,
    'root': genpass(),
}

def server_prepare():
    sudo('apt-get update && apt-get -y dist-upgrade')
    fabtools.require.apache.server()
    fabtools.require.deb.packages(['libapache2-mod-wsgi', 'python-mysqldb', 'git'])
    sudo('wget https://bootstrap.pypa.io/ez_setup.py')
    sudo('python ez_setup.py')
    sudo('rm -f ez_setup.py setuptools*')
    sudo('easy_install markdown html5lib python-openid South python-memcached django==1.6.0 django-debug-toolbar==1.0 django-endless-pagination pytz')
    install_mysql()


def setup_project():
    if fabtools.files.is_dir(env.project_dir):
        sudo('rm -rf ' + env.project_dir)
    run('mkdir -p ' + env.project_dir)
    with cd(env.project_dir):
        run('git clone https://github.com/dzone/osqa.git .')
    setup_domain()
    upload_config()
    #sudo('python manage.py syncdb --all')
    #sudo('python manage.py migrate forum --fake')
    with cd(env.home):
        sudo('chown -R %s:www-data %s' % (env.user,env.project))
        sudo('chmod -R g+w %s/forum/upfiles' % env.project)
        sudo('chmod -R g+w %s/log' % env.project)
    fabtools.service.restart("apache2")


def upload_config():
    upload_template(
            Path(env.local,'app','osqa.wsgi'),
            Path(env.project_dir,'osqa.wsgi'),
            use_sudo=True,
            context={'home': env.home, 'docroot': env.project_dir, 'project':env.project}
        )
    upload_template(
            'settings_local.py',
            Path(env.project_dir),
            context={'db_host': env.db['host'], 'db_port': env.db['port'], 'db_name': env.db['name'],
                     'db_user': env.db['user'], 'db_password': env.db['pass'], 'db_driver': env.db['driver'],
                     'admin': env.admin['email'], 'domain': env.domain
                    },
            use_jinja=True,
            template_dir=Path(env.local,'app'),
            use_sudo=True
        )


def setup_domain():
    sudo('rm -f /etc/apache2/sites-available/default*\
            /etc/apache2/sites-available/default-ssl*\
            /etc/apache2/sites-enabled/000-default*')
    fabtools.require.apache.site(env.project,
                                template_source=Path(env.local,'apache','site.conf'),
                                domain=env.domain,
                                docroot=env.project_dir,
                                port = 80,
                                admin = env.admin['email']
                                )
    fabtools.require.service.start('apache2')


def setup():
    server_prepare()
    setup_project()
    report()


def report():
    print(green('You can access your site by URL http://%s/' % env.site['domain']))
    print(green('------------------------------------'))
    print('\n')
    print(green('MYSQL database'))
    print(green('------------------------------------'))
    print('Host: %s' % env.db['host'])
    print('Database name: %s' % env.db['name'])
    print('Database user: %s' % env.db['user'])
    print('Database user password: %s' % env.db['pass'])
    print('\n')
    print(green('Superuser'))
    print(green('------------------------------------'))
    print('Login: %s' % env.admin['login'])
    print('Password: %s' % env.admin['password'])
from fabric.api import *
from unipath import Path
from contextlib import contextmanager
from fabric.contrib.files import exists
from fabric.contrib.files import upload_template
from fabric.api import settings
from fabric.colors import green

class FabricException(Exception):
    pass


def docker():
    env.hosts = ['localhost']
    env.user = 'root'


env.project = 'optera'
env.git = 'git@bitbucket.org:worldevops-Web/mautic.git'

LOCAL_ROOT_DIR = Path(__file__).ancestor(1)
env.directory = Path('/var/www/html/', env.project)

def install_composer():
    run('curl -sS https://getcomposer.org/installer|php')

def install_mosaico():
    put(Path(LOCAL_ROOT_DIR, "plugins", "pack.tar.gz"), Path(env.directory, 'plugins'))
    with cd('plugins'):
        run('tar -xf pack.tar.gz')
        run('rm -f pack.tar.gz')

def setup():
    sudo('apt-get install -y git')
    sudo('apt-get install -y vim libpcre3 libpcre3-dev')
    sudo('apt-get install -y nodejs')
    sudo('sudo npm install npm -g')
    sudo("rm -rf %s" % env.directory)
    sudo("mkdir %s" % env.directory, user=env.user)

    with cd(env.directory):
        run('git clone %s .' % env.git)
        localp = Path('/', LOCAL_ROOT_DIR, "app", "config", "local.php")
        config = Path(env.directory,'app', 'config', 'local.php')
        put(localp, config)
        install_composer()
        run('php composer.phar install')
        run('php app/console cache:clear --env=prod')
        install_mosaico()
        run('php app/console mautic:assets:generate')
        run('php app/console doctrine:schema:update --force')

    with cd(env.directory.parent):
        sudo('chown %s.www-data -R %s' % (env.user, env.project))
        sudo('chmod go+w -R %s/app/cache' % env.project)
        sudo('chmod go+w -R %s/app/logs' % env.project)

    restart_services()

def restart_services():
    with settings(abort_exception = FabricException):
        try:
            sudo('killall uwsgi')
        except FabricException:
            pass
    sudo("service nginx reload")
    sudo("service nginx restart")


def deploy_nginx():
    nginx_conf = "/etc/nginx/sites-available/%s.conf" % env.project
    sudo("rm -f %s" % nginx_conf)
    if 'vagrant' not in env.user:
        put(Path(LOCAL_ROOT_DIR, "nginx", "production.conf"), nginx_conf, use_sudo=True)
    else:
        put(Path(LOCAL_ROOT_DIR, "nginx", "template.conf"), nginx_conf, use_sudo=True)

    sudo("chown root:root %s" % nginx_conf)
    sudo("rm -f /etc/nginx/sites-enabled/%s.conf" % env.project)
    sudo("ln -s %s /etc/nginx/sites-enabled/%s.conf" %
         (nginx_conf, env.project))
    restart_services()

def deploy():
    with cd(env.directory):
        run('git pull')
        run('php app/console cache:clear --env=prod')
        run('php app/console doctrine:schema:update --force')
        run('php app/console mautic:assets:generate')
        restart_services()
        green('Done')

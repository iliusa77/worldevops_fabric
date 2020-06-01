"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10,project={project_name},http_server={apache or nginx} setup

"""
from fabric.api import *
from fabtools import require
import requests
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
import hashlib
import sys
root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *

env.project = 'dokuwiki'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))


env.app = {
    'title': 'DokuWiki',
    'lang': 'en',
    'superuser': 'admin',
    'name': 'admin',
    'password': genpass(),
    'realname': 'Administrator Wiki',
    'email': 'youremail@email.com'
}


def prepare_nginx_server():
    sudo('apt-get update && apt-get -y dist-upgrade')
    fabtools.require.nginx.server()
    common_setup()
    setup_mail_server()
    fabtools.require.deb.packages([
        'php5-fpm','zip'
    ])
    upload_php_config()
    fabtools.require.git.command()


def prepare_apache_server():
    sudo('apt-get update && apt-get -y dist-upgrade')
    fabtools.require.apache.server()
    fabtools.require.apache.module_enabled('rewrite')
    common_setup()
    setup_mail_server()
    fabtools.require.deb.packages([
        'php5','zip'
    ])
    fabtools.require.git.command()


def upload_php_config():
    put(Path(env.local, 'php', 'php-fpm.ini'), '/etc/php5/fpm/php.ini', use_sudo=True)
    fabtools.service.stop('php5-fpm')
    fabtools.service.start('php5-fpm')


def upload_config():
    put(Path(env.local,'app','acl.auth.php'), Path(env.project_dir,'conf'), use_sudo=True)
    put(Path(env.local,'app','dokuwiki.php'), Path(env.project_dir,'conf'), use_sudo=True)
    put(Path(env.local,'app','.htaccess'), Path(env.project_dir), use_sudo=True)
    upload_template(
        Path(env.local,'app','users.auth.php'),
        Path(env.project_dir,'conf'),
        use_sudo=True,
        context={'name': env.app['name'], 'pass': hashlib.md5(env.app['password']).hexdigest(), 'realname': env.app['realname'], 'email': env.app['email']}
    )
    upload_template(
        Path(env.local,'app','local.php'),
        Path(env.project_dir,'conf'),
        use_sudo=True,
        context={'title': env.app['title'], 'lang': env.app['lang'], 'superuser': env.app['superuser']}
    )
    print(green('Config uploaded'))


def setup_domain(stype):
    if stype == 'nginx':
        fabtools.require.nginx.site(env.project,
                           template_source=Path(env.local,'nginx','production.conf'),
                           domain=env.domain,
                           docroot=env.project_dir
                           )
        fabtools.require.service.start('nginx')
    if stype == 'apache':
        fabtools.require.apache.site(env.project,
                            template_source=Path(env.local,'apache','site.conf'),
                            domain=env.domain,
                            docroot=env.project_dir,
                            port = 80
                            )
        fabtools.require.service.start('apache2')


def chmod():
    with cd(env.project_dir):
        sudo('chmod -R 777 conf data')


def setup_project():
    if fabtools.files.is_dir(env.project_dir):
        sudo('rm -rf ' + env.project_dir)
    run('mkdir -p ' + env.project_dir)
    with cd(env.project_dir):
        run('wget http://download.dokuwiki.org/src/dokuwiki/dokuwiki-stable.tgz')
        run('tar zxvf dokuwiki-stable.tgz')
        run('\'cp\' -af dokuwiki-*/* %s' %env.project_dir)
        run('rm -f install.php')
        run('rm -rf dokuwiki-*')
    chmod()


def setup_with_apache():
    prepare_apache_server()
    setup_project()
    setup_domain('apache')
    upload_config()
    print(green('Done'))
    report()


def setup_with_nginx():
    prepare_nginx_server()
    setup_project()
    setup_domain('nginx')
    upload_config()
    print(green('Done'))
    report()


def setup():
    if env.http_server == 'nginx':
        setup_with_nginx()
    else:
        setup_with_apache()

def report():
    print(green('You can access your site by URL http://%s/' % env.domain))
    print(green('------------------------------------'))
    print('\n')
    print(green('Superuser'))
    print(green('------------------------------------'))
    print('Login: %s' % env.app['superuser'])
    print('Password: %s' % env.app['password'])

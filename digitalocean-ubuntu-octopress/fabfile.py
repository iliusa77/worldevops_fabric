from fabric.api import sudo, env, cd
import fabtools
from unipath import Path
from fabric.contrib.files import upload_template

commonname = 'octopress33.com'
home = Path('/', 'home', env.user)
project = Path(home, commonname)

env.site = {
    'domain': commonname,  # without www.
    'docroot': Path(project, 'public')
}

def install_ruby():
    sudo('apt-add-repository ppa:brightbox/ruby-ng -y')
    sudo('apt-get update')
    sudo('apt-get install ruby2.3 ruby2.3-dev git nodejs -y')

def install_octopress():
    with cd(home):
        sudo('git clone git://github.com/imathis/octopress.git {}'.format(commonname))
    with cd(project):
        sudo('gem install bundler execjs')
        sudo('bundle install')
        sudo('rake install')
        sudo('rake generate')

def setup_nginx():
    fabtools.require.nginx.server()
    upload_template(
        filename=Path('./', 'nginx', 'site.conf'),
        destination='/etc/nginx/sites-available/{}.conf'.format(commonname),
        context=env.site, use_sudo=True
        )
    sudo("ln -s /etc/nginx/sites-available/{0}.conf /etc/nginx/sites-enabled/{0}.conf".format(commonname))
    fabtools.service.reload('nginx')

def setup():
    install_ruby()
    install_octopress()
    setup_nginx()
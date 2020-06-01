from decorator import contextmanager
from fabric.api import sudo, cd, run, env, prefix
import fabtools
from fabtools import require
from unipath import Path
from fabric.contrib.files import upload_template

project_name = 'pelican33'
commonname = 'pelican33.com'
home = Path('/', 'home', env.user)
project = Path(home, project_name)
activate_path = Path(project, 'env', 'bin', 'activate')
activate = 'source {}'.format(activate_path)

env.site = {
    'domain': commonname,  # without www.
    'docroot': Path(project, 'output')
}

@contextmanager
def source_virtualenv():
    with prefix(activate):
        yield


def setup():
    sudo('apt-get update')
    require.deb.packages([
        'python-pip', 'python-virtualenv'
    ])

    with cd(home):
        run('mkdir {}'.format(project))
        with cd(project):
            run('virtualenv env')
            with source_virtualenv():
                run('pip install --upgrade pelican Markdown')
                run('pelican-quickstart')
                upload_template(
                filename=Path('./', 'content', 'post.rst'),
                destination='{}/content/post.rst'.format(project)
                )
                run('make html')
    setup_nginx()

def setup_nginx():
    fabtools.require.nginx.server()
    #with cd('/usr/share/nginx'):
    #    sudo('rm -r html && ln -s {}/output html'.format(project))
    upload_template(
        filename=Path('./', 'nginx', 'site.conf'),
        destination='/etc/nginx/sites-available/{}.conf'.format(commonname),
        context=env.site, use_sudo=True
        )
    sudo("ln -s /etc/nginx/sites-available/{0}.conf /etc/nginx/sites-enabled/{0}.conf".format(commonname))
    fabtools.service.reload('nginx')


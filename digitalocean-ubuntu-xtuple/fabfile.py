from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path


class FabricException(Exception):
    pass


def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))

env.user = 'vagrant'
env.password = 'vagrant'

env.hosts = [
    'demo.loc'
]
env.project = 'xtuple'
env.hostname = "www.%s.com" % env.project
env.site = {
    'domain': "demo.loc"
}

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': genpass(),
    'port': 3306,
    'root': genpass()
}
env.cert_path = Path("/", "etc", "ssl", "nginx")


def install_project():
    # sudo("apt-get update && apt-get -y dist-upgrade")
    sudo("apt-get install -y git")
    fabtools.git.clone("https://github.com/xtuple/xtuple-admin-utility.git %s" % env.project_dir)
    with cd(env.project_dir):
        sudo("./xtuple-utility.sh -a")
    fabtools.require.nginx.server()
    create_ssl_cert()
    config_nginx()
    credentials()


def config_nginx():
    with open('./nginx/site.conf') as fn:
        config_tpl = fn.read()
    require.nginx.site(
        env.project,
        template_contents=config_tpl,
        port=80,
        hostname=env.site['domain'],
        cert_path=env.cert_path+"/"+env.project,

    )
    require.nginx.enabled(env.project)


def create_ssl_cert():
    fabtools.require.files.directory(env.cert_path, use_sudo=True)
    with cd(env.cert_path):
        sudo("openssl req -x509 -nodes -days 365 -newkey rsa:2048 -subj \"/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.%s\" -keyout %s/%s.key -out %s/%s.crt" % (env.site['domain'], env.cert_path, env.project, env.cert_path, env.project))


def credentials():
    run("clear")
    print ("Done")
    print("Visit https://%s" % env.site['domain'])
    print("Login - admin")
    print("Password - admin")
    print("Please don't forget to change admin password")


def destroy_nginx():
    fabtools.service.stop('nginx')
    fabtools.deb.uninstall(['nginx'], purge=True, options=None)
    sudo('rm -f /etc/nginx/sites-available/*')
    sudo('rm -f /etc/nginx/sites-enabled/*')
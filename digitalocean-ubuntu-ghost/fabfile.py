from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import blue, green, red


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
env.project = 'ghost'
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
    'pass': '123123',
    'port': 3306,
    'root': '123123'
}


def install_mysql():
    require.mysql.server(password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        query = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (env.db['user'], env.db['pass'])
        fabtools.mysql.query(query=query, use_sudo=True)
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.database(env.db['name'], owner=env.db['user'])


def install_pgsql():
    fabtools.require.postgres.server()
    fabtools.require.postgres.user(env.db['user'], env.db['pass'])
    fabtools.require.postgres.database(env.db['name'], owner=env.db['user'])
    fabtools.require.service.started('postgresql')


def install_nodejs():
    require.deb.packages(["nodejs", 'npm'])
    fabtools.files.symlink(source="/usr/bin/nodejs", destination="/usr/bin/node", use_sudo=True)


def install_project():
    run("curl -L https://ghost.org/zip/ghost-latest.zip -o ghost.zip")
    sudo("apt-get install unzip")
    run("mkdir %s" % env.project)
    run("unzip ghost.zip -d %s" % env.project_dir)
    with cd(env.project_dir):
        run("npm install --production")

        if _mysql_is_installed():
            source = Path(Path(__file__).ancestor(1), 'config', 'mysql.config.js')
            destination = Path(env.project_dir, 'config.js')
            upload_template(
                filename=source,
                destination=destination,
                context={
                    'hostname': env.site['domain'],
                    'host': env.db['host'],
                    'user': env.db['user'],
                    'password': env.db['pass'],
                    'name': env.db['name']
                },
                use_sudo=True,
            )
        elif _pgsql_is_installed():
            source = Path(Path(__file__).ancestor(1), 'config', 'pg.config.js')
            destination = Path(env.project_dir, 'config.js')
            upload_template(
                filename=source,
                destination=destination,
                context={
                    'hostname': env.site['domain'],
                    'port': '5432',
                    'host': env.db['host'],
                    'user': env.db['user'],
                    'password': env.db['pass'],
                    'name': env.db['name']
                },
                use_sudo=True,
            )
        else:
            source = Path(Path(__file__).ancestor(1), 'config', 'sqlite.config.js')
            destination = Path(env.project_dir, 'config.js')
            upload_template(
                filename=source,
                destination=destination,
                context={
                    'hostname': env.site['domain']
                },
                use_sudo=True,
            )
        sudo("npm install -g pm2")
        run("echo \"export NODE_ENV=production\" >> ~/.profile")
        run("source ~/.profile")
        run("pm2 kill")
        run("pm2 start index.js --name ghost")


def _mysql_is_installed():
    with settings(hide('stderr'), warn_only=True):
        output = run('mysql --version')
    return output.succeeded


def _pgsql_is_installed():
    with settings(hide('stderr'), warn_only=True):
        output = run('psql --version')
    return output.succeeded


def config_apache():
    require.apache.enable_module("proxy")
    require.apache.enable_module("proxy_http")
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()
    require.apache.site(
        env.site['domain'],
        template_contents=config_tpl,
        port=80,
        hostname=env.site['domain'],
        document_root=env.project_dir
    )


def config_nginx():
    with open('./nginx/site.conf') as fn:
        config_tpl = fn.read()
    require.nginx.site(
        env.project,
        template_contents=config_tpl,
        port=80,
        hostname=env.site['domain']
    )
    require.nginx.enabled(env.project)


def credentials():
    run("clear")
    print (red("-----------------------------------"))
    print(red("To create admin account visit - http://%s/ghost" % env.site['domain']))
    print(red("Project available on url - http://%s" % env.site['domain']))


def setup_apache_sqlite():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    config_apache()
    install_nodejs()
    install_project()
    credentials()


def setup_apache_mysql():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    config_apache()
    install_mysql()
    install_nodejs()
    install_project()
    credentials()


def setup_apache_postgres():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    config_apache()
    install_pgsql()
    install_nodejs()
    install_project()
    credentials()


def setup_nginx_sqlite():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.nginx.server()
    config_nginx()
    install_nodejs()
    install_project()
    credentials()


def setup_nginx_mysql():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.nginx.server()
    config_nginx()
    install_mysql()
    install_nodejs()
    install_project()
    credentials()


def setup_nginx_postgres():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.nginx.server()
    config_nginx()
    install_pgsql()
    install_nodejs()
    install_project()
    credentials()

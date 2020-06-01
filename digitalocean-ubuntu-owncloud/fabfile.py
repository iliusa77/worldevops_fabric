from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path
from fabric.contrib.files import upload_template


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
env.project = 'owncloud'
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


def install_mysql():
    require.mysql.server(password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        query = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (env.db['user'], env.db['pass'])
        fabtools.mysql.query(query=query, use_sudo=True)
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.database(env.db['name'], owner=env.db['user'])


def config_apache():
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()
    require.apache.site(
        '%s.com' % env.project,
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
            docroot=env.project_dir,
            hostname=env.site['domain'],
            cert_path=env.cert_path+"/"+env.project
        )
        require.nginx.enabled(env.project)


def install_pgsql():
    fabtools.require.postgres.server()
    fabtools.require.postgres.user(env.db['user'], env.db['pass'])
    fabtools.require.postgres.database(env.db['name'], owner=env.db['user'])
    fabtools.require.service.started('postgresql')


def create_ssl_cert():
    fabtools.require.files.directory(env.cert_path, use_sudo=True)
    with cd(env.cert_path):
        sudo("openssl req -x509 -nodes -days 365 -newkey rsa:2048 -subj \"/C=US/ST=Denial/L=Springfield/O=Dis/CN=www.%s\" -keyout %s/%s.key -out %s/%s.crt" % (env.site['domain'], env.cert_path, env.project, env.cert_path, env.project))


def credentials():
    run("clear")
    print ("Done!")
    print ("-----------------------------------")
    print ("Database Config :")
    print ("Db-Name: %s" % env.db['name'])
    print ("Db-User: %s" % env.db['user'])
    print ("Db-Password: %s" % env.db['pass'])


def setup_apache_mysql():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    install_mysql()
    run("wget -nv https://download.owncloud.org/download/repositories/stable/xUbuntu_14.04/Release.key -O Release.key")
    sudo("apt-key add - < Release.key")
    sudo("sh -c \"echo \'deb http://download.owncloud.org/download/repositories/stable/xUbuntu_14.04/ /\' >> /etc/apt/sources.list.d/owncloud.list\"")
    sudo("apt-get update")
    sudo("apt-get install -y owncloud")
    sudo("mv /var/www/owncloud %s" % env.project_dir)
    config_apache()
    credentials()


def setup_apache_pgsql():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    install_pgsql()
    run("wget -nv https://download.owncloud.org/download/repositories/stable/xUbuntu_14.04/Release.key -O Release.key")
    sudo("apt-key add - < Release.key")
    sudo(
        "sh -c \"echo \'deb http://download.owncloud.org/download/repositories/stable/xUbuntu_14.04/ /\' >> /etc/apt/sources.list.d/owncloud.list\"")
    sudo("apt-get update")
    sudo("apt-get install -y owncloud")
    sudo("mv /var/www/owncloud %s" % env.project_dir)
    config_apache()
    credentials()


def setup_nginx_mysql():
    sudo("apt-get update && apt-get -y dist-upgrade")
    install_mysql()
    run("wget -nv https://download.owncloud.org/download/repositories/stable/xUbuntu_14.04/Release.key -O Release.key")
    sudo("apt-key add - < Release.key")
    sudo("sh -c \"echo \'deb http://download.owncloud.org/download/repositories/stable/xUbuntu_14.04/ /\' >> /etc/apt/sources.list.d/owncloud.list\"")
    sudo("apt-get update")
    sudo("apt-get install -y owncloud")
    sudo("mv /var/www/owncloud %s" % env.project_dir)
    sudo("service apache2 stop")
    sudo("update-rc.d -f apache2 disable")
    fabtools.require.nginx.server()
    require.deb.packages(["php5-fpm"])
    create_ssl_cert()
    config_nginx()
    credentials()


def setup_nginx_pgsql():
    install_pgsql()
    run("wget -nv https://download.owncloud.org/download/repositories/stable/xUbuntu_14.04/Release.key -O Release.key")
    sudo("apt-key add - < Release.key")
    sudo("sh -c \"echo \'deb http://download.owncloud.org/download/repositories/stable/xUbuntu_14.04/ /\' >> /etc/apt/sources.list.d/owncloud.list\"")
    sudo("apt-get update")
    sudo("apt-get install -y owncloud")
    sudo("mv /var/www/owncloud %s" % env.project_dir)
    sudo("service apache2 stop")
    sudo("update-rc.d -f apache2 disable")
    require.deb.packages(["php5-fpm"])
    create_ssl_cert()
    config_nginx()
    credentials()

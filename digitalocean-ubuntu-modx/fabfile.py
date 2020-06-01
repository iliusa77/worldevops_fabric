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
env.project = 'modx'
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

env.manager = {
    'admin_name': 'Admin',
    'admin_pass': genpass(),
    'admin_email': 'admin@%s' % env.site['domain']
}
env.php_version = "5"


def install_mysql():
    require.mysql.server(password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        query = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (env.db['user'], env.db['pass'])
        fabtools.mysql.query(query=query, use_sudo=True)
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.database(env.db['name'], owner=env.db['user'])


def install_project():
    require.deb.packages(["unzip"])
    run("wget https://modx.com/download/direct/modx-2.5.0-pl.zip")
    run("unzip modx-2.5.0-pl.zip")
    run("mv modx-2.5.0-pl modx")


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
    if env.php_version == "7":
        with open('./nginx/site7.conf') as fn:
            config_tpl = fn.read()
    else:
        with open('./nginx/site.conf') as fn:
            config_tpl = fn.read()
    require.nginx.site(
        env.project,
        template_contents=config_tpl,
        port=80,
        docroot=env.project_dir,
        hostname=env.site['domain']
    )
    require.nginx.enabled(env.project)


def config_project():
    source = Path(Path(__file__).ancestor(1), 'config', "config.xml")
    destination = Path(env.project_dir, "setup", "config.xml")
    upload_template(
        filename=source,
        destination=destination,
        context={
            'host': env.db['host'],
            'db_type': 'mysql',
            'db_name': env.db['name'],
            'db_user': env.db['user'],
            'db_pass': env.db['pass'],
            'admin_name': env.manager['admin_name'],
            'admin_pass': env.manager['admin_pass'],
            'admin_email': env.manager['admin_email'],
            'project_dir': env.project_dir,
        },
    )
    with cd(env.project_dir):
        run("php setup/index.php --installmode=new")
        run("chmod -R 0777 core/cache/")


def credentials():
    run("clear")
    print ("Done!")
    print ("-----------------------------------")
    print("Visit http://%s" % env.site['domain'])
    print ("-----------------------------------")
    print ("Database Config :")
    print ("Db-Name: %s" % env.db['name'])
    print ("Db-User: %s" % env.db['user'])
    print ("Db-Password: %s" % env.db['pass'])
    print ("-----------------------------------")
    print ("Manager parameters :")
    print ("Username - %s" % env.manager['admin_name'])
    print ("Password - %s" % env.manager['admin_pass'])
    print ("Email - %s" % env.manager['admin_email'])


def setup_apache_php5_5():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    require.deb.packages(["php5", "php5-mysql"])
    install_mysql()
    install_project()
    config_apache()
    config_project()
    credentials()


def setup_apache_php5_6():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    sudo("add-apt-repository -y ppa:ondrej/php5-5.6")
    sudo("apt-get -y update")
    require.deb.packages(["php5", "php5-mysql"])
    install_mysql()
    install_project()
    config_apache()
    config_project()
    credentials()


def setup_apache_php7():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    sudo("add-apt-repository -y ppa:ondrej/php")
    sudo("apt-get update")
    require.deb.packages(["php7.0", "php7.0-mysql", "php7.0-xml"])
    fabtools.require.apache.module_enabled("php7.0")
    fabtools.require.apache.module_enabled("mpm_prefork")
    env.php_version = "7"
    install_mysql()
    install_project()
    config_apache()
    config_project()
    credentials()


def setup_nginx_php5_5():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.nginx.server()
    require.deb.packages(["php5", "php5-mysql", "php5-fpm", "php5-cli"])
    install_mysql()
    install_project()
    config_nginx()
    config_project()
    credentials()


def setup_nginx_php5_6():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.nginx.server()
    sudo("add-apt-repository -y ppa:ondrej/php5-5.6")
    sudo("apt-get -y update")
    require.deb.packages(["php5", "php5-mysql", "php5-fpm"])
    install_mysql()
    install_project()
    config_nginx()
    config_project()
    credentials()


def setup_nginx_php7():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.nginx.server()
    sudo("add-apt-repository -y ppa:ondrej/php")
    sudo("apt-get update")
    require.deb.packages(["php7.0", "php7.0-mysql", "php7.0-fpm", "php7.0-xml"])
    env.php_version = "7"
    install_mysql()
    install_project()
    config_nginx()
    config_project()
    credentials()

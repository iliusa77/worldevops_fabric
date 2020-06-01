from fabric.api import *
from fabtools import require, apache
import fabtools
from unipath import Path
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
    'demo.loc',
]
env.project = 'prestashop'
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
env.admin = {
    'email': 'admin@%s.com' % env.project,
    'password': genpass()

}

env.conf = {'DB_PASSWD': 'rootpwd'}


def install_apache():
    fabtools.require.apache.server()


def install_php_apache():
    require.deb.packages(
        ["php5", "php5-gd", "php5-mcrypt", "php5-mysql", "php5-curl", "php5-intl"]
    )
    sudo('php5enmod mcrypt')
    fabtools.apache.enable_module("rewrite")


def install_mysql():
    require.mysql.server(password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        query = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (env.db['user'], env.db['pass'])
        fabtools.mysql.query(query=query, use_sudo=True)
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.database(env.db['name'], owner=env.db['user'])


def install_prestashop():
    sudo("wget http://www.prestashop.com/download/releases/prestashop_1.6.1.5.zip")
    sudo("apt-get install unzip")
    run("unzip prestashop_1.6.1.5.zip ")
    sudo("rm prestashop_1.6.1.5.zip")
    sudo("chmod 0777 -R  %s" % env.project_dir)

    # sudo("curl -sS https://getcomposer.org/installer | php")
    # sudo("mv composer.phar /usr/local/bin/composer")
    # sudo("apt-get install -y git")
    # with cd(env.home):
    #     fabtools.git.clone("https://github.com/PrestaShop/PrestaShop.git", path=env.project)
    #     sudo("chmod 0777 -R  %s" % env.project_dir)
    # source = Path(Path(__file__).ancestor(1), env.project, 'parameters.yml')
    # destination = Path(env.project_dir, "app", "config")
    # upload_template(
    #     filename=source,
    #     destination=destination,
    #     context={
    #         'db_host': env.db['host'],
    #         'db_port': env.db['port'],
    #         'db_name': env.db['name'],
    #         'db_user': env.db['user'],
    #         'db_pass': env.db['pass'],
    #     },
    #     use_sudo=True,
    # )
    # with cd(env.project_dir):
    #     run("composer install")


def config_site_apache():
    fabtools.require.apache.site_disabled('000-default')
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()
    require.apache.site(
        '%s.com' % env.project,
        template_contents=config_tpl,
        port=80,
        hostname=env.site['domain'],
        document_root=env.project_dir
    )


def config_site_nginx():
    fabtools.require.nginx.disabled('default')
    with open('./nginx/site.conf') as fn:
        config_tpl = fn.read()
    require.nginx.site(env.project,
                       template_contents=config_tpl,
                       port=80,
                       docroot=env.project_dir
                       )
    require.nginx.enabled(env.project)


def deploy():
    path_install_script = Path('prestashop', "install")
    print (path_install_script)
    with cd(path_install_script):
        run("php index_cli.php "
            "--domain=%s "
            "--db_server=%s "
            "--db_name=%s "
            "--db_user=%s "
            "--db_password=%s "
            "--firstname=%s "
            "--lastname=%s "
            "--password=%s "
            "--email=%s "
            "--activity=%s "
            % (env.site['domain'], env.db['host'], env.db['name'], env.db['user'], env.db['pass'],
               'admin', 'admin', env.admin['password'], env.admin['email'], '1')
            )
    with cd(env.project_dir):
        sudo("rm -r install")
        # admin_path =
    sudo("chmod 0777 -R  %s" % env.project_dir)


def report():
    print(green("Done"))
    run("clear")
    print(red("MYSQL database"))
    print (red("-----------------------------------"))
    print("host:  %s" % env.site['domain'])
    print("login:  %s" % env.db['user'])
    print("pass:  %s" % env.db['pass'])
    print (red("-----------------------------------"))
    print (blue("Administrating tool %s/admin") % env.site['domain'])
    print("login/email:  %s" % env.admin['email'])
    print("pass:  %s" % env.admin['password'])


def setup_apache():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    print(blue('Apache installed'))
    require.deb.packages(["php5", "php5-gd", "php5-mcrypt", "php5-mysql", "php5-curl", "php5-intl"])
    install_mysql()
    install_prestashop()
    config_site_apache()
    deploy()
    report()


def setup_nginx():
    sudo("apt-get update && apt-get -y dist-upgrade")
    sudo("apt-get install -y git")
    fabtools.require.nginx.server()
    print(blue('Nginx installed'))
    require.deb.packages(["php5-cli", "php5-gd", "php5-mcrypt", "php5-mysql", "php5-curl", "php5-intl", "php5-fpm"])
    print(blue('PHP installed'))
    install_mysql()
    config_site_nginx()
    install_prestashop()
    deploy()
    report()

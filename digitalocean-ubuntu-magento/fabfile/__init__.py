"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10 setup_apache

"""
from fabtools import require
from unipath import Path
from fabric.colors import red
from fabric.contrib.files import upload_template
import sys
root = Path(__file__).ancestor(3)
sys.path.append(root)
from worldevops import *
from fabric.colors import blue, yellow, green, red

env.project = 'magento'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)
env.local = Path(Path(__file__).ancestor(2))

env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': '123123',
    'port': 3306,
    'root': '123123'
}


def install_mysql():
    fabtools.require.mysql.server(version='5.6', password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        query = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (env.db['user'], env.db['pass'])
        fabtools.mysql.query(query=query, use_sudo=True)
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.database(env.db['name'], owner=env.db['user'])


def install_magento():
    sudo("curl -sS https://getcomposer.org/installer | php")
    sudo("mv composer.phar /usr/local/bin/composer")

    with cd(env.home):
        fabtools.git.clone("https://github.com/magento/magento2.git", path=env.project)
        sudo("chmod 0755 -R  %s" % env.project_dir)
        with cd(env.project):
            # token: c08f3d2dd712ff6f14f888c2a0502090413279ba
            run("composer install")
            sudo("chmod -R 0777 var/ pub/media/ pub/static app/etc/")


def config_site_apache():
    fabtools.require.apache.site_disabled('000-default')
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()

    fabtools.require.apache.site(
        '%s.com' % env.project,
        template_contents=config_tpl,
        port=80,
        hostname=env.domain,
        document_root=env.project_dir
    )


def config_site_nginx():
    fabtools.require.nginx.disabled('default')
    with open('./nginx/site.conf') as fn:
        config_tpl = fn.read()
    fabtools.require.nginx.site(env.project,
                       template_contents=config_tpl,
                       port=80,
                       docroot=env.project_dir
                       )
    fabtools.require.nginx.enabled(env.project)


def reindex_clear_cache():
    with cd(env.project_dir):
        sudo("php bin/magento indexer:reindex")
        sudo("php bin/magento cache:clean")
        print (yellow("Done!"))


def print_info():
    print(green("Done"))
    run("clear")
    print(red("MYSQL database"))
    print (red("-----------------------------------"))
    print("host:  %s" % env.hosts)
    print("login:  %s" % env.db['user'])
    print("pass:  %s" % env.db['pass'])
    print (blue("Please visit http://%s/setup/ to complete installation") % env.domain)
    print (blue("When login into admin panel, execute [fab reindex_clear_cache]"))
    print (blue("If you need testing dada, execute [fab performance_testing_data]"))


def performance_testing_data():
    with cd(env.project_dir):
        magento = Path(env.project_dir, "bin", "magento")
        data_xml_path = Path(env.project_dir, "setup", "performance-toolkit", "profiles", "ce",)
        sudo("php %s setup:perf:generate-fixtures %s/small.xml" % (magento, data_xml_path))
        sudo("php %s cache:clean" %magento)
        sudo("chmod -R 0777 var/ pub/media/ pub/static app/etc/")


def setup_apache():
    sudo('apt-get update && apt-get -y dist-upgrade')
    sudo("apt-get install -y git")
    fabtools.require.apache.server()
    print(blue('Apache installed'))
    sudo("a2enmod rewrite")
    fabtools.service.reload('apache2')
    sudo("add-apt-repository -y ppa:ondrej/php5-5.6")
    sudo("apt-get update")
    fabtools.require.deb.packages([
        'libapache2-mod-php5', 'php5', 'php5-mcrypt', 'php5-curl',
        'php5-cli', 'php5-mysql', 'php5-gd', 'php5-intl', 'php5-xsl'
    ])
    with open('./php/php.ini') as fn:
        config = fn.read()
    fabtools.require.file('/etc/php5/apache2/php.ini', contents=config, use_sudo=True)
    print(blue('PHP installed'))
    install_mysql()
    install_magento()
    config_site_apache()
    fabtools.cron.add_daily('reindex', env.user, 'php %s/bin/magento indexer:reindex' % env.project_dir)
    print_info()


def setup_nginx():
    sudo('apt-get update && apt-get -y dist-upgrade')
    sudo("apt-get install -y git")
    fabtools.require.nginx.server()
    print(blue('Nginx installed'))
    sudo("add-apt-repository -y ppa:ondrej/php")
    sudo("apt-get -y update")
    sudo("apt-get -y install php5.6 php5.6-mcrypt php5.6-curl php5.6-cli php5.6-mysql php5.6-gd php5.6-intl php5.6-xsl php5.6-fpm php5.6-mbstring php5.6-zip")
    with open('./php/php.ini') as fn:
        config = fn.read()
    fabtools.require.file('/etc/php/5.6/fpm/php.ini', contents=config, use_sudo=True)
    fabtools.service.stop("php5.6-fpm")
    fabtools.service.start("php5.6-fpm")
    print(blue('PHP installed'))
    install_mysql()
    install_magento()
    config_site_nginx()
    fabtools.cron.add_daily('reindex', env.user, 'php %s/bin/magento indexer:reindex' % env.project_dir)
    print_info()


def setup_varnish_apache():
    fabtools.require.deb.package("varnish")
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()

    fabtools.require.apache.site(
        '%s.com' % env.project,
        template_contents=config_tpl,
        port=8080,
        hostname=env.domain,
        document_root=env.project_dir
    )
    source = Path(env.local, "apache", "ports.conf")
    destination = Path("/", "etc", "apache2", "ports.conf")
    upload_template(
        filename=source,
        destination=destination,
        use_sudo=True,
    )
    fabtools.service.restart("apache2")
    source = Path(env.local, "varnish", "varnish")
    destination = Path("/", "etc", "default", "varnish")
    upload_template(
        filename=source,
        destination=destination,
        use_sudo=True,
    )
    fabtools.service.restart("varnish")


def setup_varnish_nginx():
    fabtools.require.deb.package("varnish")
    fabtools.require.nginx.disabled('default')
    with open('./nginx/site.conf') as fn:
        config_tpl = fn.read()
    fabtools.require.nginx.site(env.project,
                                template_contents=config_tpl,
                                port=8080,
                                docroot=env.project_dir
                                )
    fabtools.require.nginx.enabled(env.project)
    source = Path(env.local, "varnish", "varnish")
    destination = Path("/", "etc", "default", "varnish")
    upload_template(
        filename=source,
        destination=destination,
        use_sudo=True,
    )
    fabtools.service.restart("varnish")





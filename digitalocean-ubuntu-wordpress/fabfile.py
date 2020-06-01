from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green, red


class FabricException(Exception):
    pass


def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))


env.hosts = [
    'demo.loc'
 ]
env.project = 'wordpress'

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

env.wp_defines = {
    'AUTH_KEY': 'Y[ZjcA(#VtCgv$N.otIq!l7/C!ORYgS=GQ{tI9xVq$YL`Au!0s_1w02*Xq8O/_f{',
    'SECURE_AUTH_KEY': 'c:1*8o@i%z=^dZI.K:5Mn2]Xr@83:m3EZe0<k0e3PH/K%FV q[&.$pMY9k*.QKv^',
    'LOGGED_IN_KEY': 's?>hp:6IV8N>&%IFdf/#HW]Hl76o7Vw,6]Xw;4Y_IsN#|k#Q{ IW!jm>|t<+<mOK',
    'NONCE_KEY': 'GFk.=p?IRyE#P6e<ttymdXJ.it*[ZG9~h72u&5k(z]e-w=#!uz_>v!3NM3MYyPe7',
    'AUTH_SALT': 'G[F9n~C({#cqqA.LI6u+gVi:$s=ziyvcqp59}7+s`h}5]]gkA:Xkj&//j*E?E@Iq',
    'SECURE_AUTH_SALT': 'P%d@0E1/}ms|M$@&B:}!,P<hEqKaR,v4miFcA^]MN[On2R4wlb_^N>0bdQ%=p(f$',
    'LOGGED_IN_SALT': 'uTB(1gP6sMi^$FzwCw&$5t9AfT{}?w e1fVbEQNefz+J+s|_RaN8Alw& lPu5Xb.',
    'NONCE_SALT': '~.HdA,iuEa|v#Q6|Gp!;*Ug$p$kA]W?+,tufO5U>9J{6;ms)3ZilOHdC*d4z-T`2',
}


def install_apache():
    fabtools.require.apache.server()


def install_nginx():
    fabtools.require.nginx.server()


def install_php_for_apache():
    sudo("add-apt-repository -y ppa:ondrej/php")
    sudo("apt-get update")
    sudo("apt-get install -y php7.0 libapache2-mod-php7.0 php7.0-curl php7.0-json php7.0-gd php7.0-mbstring php7.0-zip php7.0-mysql")
    fabtools.require.apache.module_enabled("php7.0")
    fabtools.require.apache.module_enabled("mpm_prefork")
    fabtools.service.reload('apache2')


def install_php_for_nginx():
    sudo("add-apt-repository -y ppa:ondrej/php")
    sudo("apt-get update")
    sudo("apt-get install -y php7.0 php7.0-curl php7.0-json php7.0-fpm php7.0-gd php7.0-mbstring php7.0-zip php7.0-mysql")


def install_mysql():
    require.mysql.server(password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.mysql.create_user(name=env.db['user'], password=env.db['pass'], host=env.db['host'])
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.database(env.db['name'], owner=env.db['user'])


def install_wordpress():
    sudo("apt-get install -y unzip")
    run("mkdir %s" % env.project_dir)
    with cd(env.project_dir):
        run("wget https://wordpress.org/latest.zip")
        run("unzip {}/latest.zip".format(env.project_dir))
        run("mv wordpress/* {}".format(env.project_dir))
        run("rm *.zip")
    wp_config = Path(Path(__file__).ancestor(1), 'wordpress', 'wp-config.php')
    destination = env.project_dir
    upload_template(
        filename=wp_config,
        destination=destination,
        context={
            'name': env.db['name'],
            'user': env.db['user'],
            'pass': env.db['pass'],
            'AUTH_KEY': env.wp_defines['AUTH_KEY'],
            'SECURE_AUTH_KEY': env.wp_defines['SECURE_AUTH_KEY'],
            'LOGGED_IN_KEY': env.wp_defines['LOGGED_IN_KEY'],
            'NONCE_KEY': env.wp_defines['NONCE_KEY'],
            'AUTH_SALT': env.wp_defines['AUTH_SALT'],
            'SECURE_AUTH_SALT': env.wp_defines['SECURE_AUTH_SALT'],
            'LOGGED_IN_SALT': env.wp_defines['LOGGED_IN_SALT'],
            'NONCE_SALT': env.wp_defines['NONCE_SALT'],
            },
        use_sudo=True,
    )


def apache_enable_site():
    fabtools.require.apache.site_disabled('000-default')
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()

    require.apache.site(
        'wordpress.com',
        template_contents=config_tpl,
        port=80,
        hostname=env.site['domain'],
        document_root=env.project_dir,
    )


def nginx_enable_site():
    fabtools.require.nginx.disabled('default')
    with open('./nginx/site.conf') as fn:
        config_tpl = fn.read()
    require.nginx.site(env.project,
                       template_contents=config_tpl,
                       port=80,
                       docroot=env.project_dir,
                       )
    require.nginx.enabled(env.project)


def setup_apache():
    sudo("apt-get update")
    sudo("apt-get -y dist-upgrade")
    run("clear")
    install_apache()
    install_php_for_apache()
    install_mysql()
    install_wordpress()
    apache_enable_site()
    sudo("service apache2 restart")
    credentials()


def setup_nginx():
    sudo("apt-get update")
    sudo("apt-get -y dist-upgrade")
    run("clear")
    install_nginx()
    install_php_for_nginx()
    install_mysql()
    install_wordpress()
    nginx_enable_site()
    credentials()


def setup_memcache():
    run("cd ~")
    sudo("apt-get install -y php-memcached")
    sudo("apt-get install -y php7.0-dev git pkg-config build-essential libmemcached-dev")
    run("git clone https://github.com/php-memcached-dev/php-memcached.git")
    with cd("php-memcached"):
        run('git checkout php7')
        run("phpize")
        run("./configure --disable-memcached-sasl")
        run("make")
        sudo("sudo make install")
    sudo("ln -s /etc/php/7.0/mods-available/memcached.ini /etc/php/7.0/fpm/conf.d/20-memcached.ini")
    sudo("ln -s /etc/php/7.0/mods-available/memcached.ini /etc/php/7.0/cli/conf.d/20-memcached.ini")
    sudo("service php7.0-fpm restart")


def setup_redis():
    require.redis.instance('mydb')
    print fabtools.supervisor.process_status('redis_mydb')


def setup_plugin(plugin_url):
    run("wget %s" % plugin_url)
    plugins_path = Path('wordpress', 'wp-content', 'plugins')
    run("unzip *.zip -d %s/" % plugins_path)
    run("rm *.zip")


def credentials():
    print(green("Done"))
    run("clear")
    print(red("MYSQL database"))
    print (red("-----------------------------------"))
    print("host:  %s" % env.site['domain'])
    print("login:  %s" % env.db['user'])
    print("pass:  %s" % env.db['pass'])
    print (red("-----------------------------------"))
    print ("If you want install wordpress plugin please execute [fab setup_plugin:[the_url_to_download_plugin]]")

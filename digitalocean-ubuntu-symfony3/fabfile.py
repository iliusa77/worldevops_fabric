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
    '192.168.33.10'
]
env.project = 'MusicAcademy'
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


def install_apache():
    fabtools.require.apache.server()


def install_php7():
    sudo("add-apt-repository -y ppa:ondrej/php")
    sudo("apt-get update")
    sudo("apt-get install -y php7.0 libapache2-mod-php7.0 php7.0-curl php7.0-json php7.0-gd php7.0-mbstring php7.0-zip php7.0-fpm php7.0-xml")
    fabtools.require.apache.module_enabled("php7.0")
    fabtools.require.apache.module_enabled("mpm_prefork")
    # fabtools.service.reload('apache2')


def install_mysql():
    require.mysql.server(password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        query = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (env.db['user'], env.db['pass'])
        fabtools.mysql.query(query=query, use_sudo=True)
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.database(env.db['name'], owner=env.db['user'])


def install_symfony3():
    sudo("apt-get install -y git")
    sudo("curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/local/bin --filename=composer")
    with cd(env.home):
        run('composer create-project symfony/framework-standard-edition %s "3.0.*"' % env.project)
        symfony_config = Path(Path(__file__).ancestor(1), 'config', 'parameters.yml')
        destination = Path(env.project_dir, 'app', 'config', 'parameters.yml')
        upload_template(
            filename=symfony_config,
            destination=destination,
            context={
                'host': env.db['host'],
                'port': env.db['port'],
                'db_name': env.db['name'],
                'db_user': env.db['user'],
                'db_pass': env.db['pass'],
            },
            use_sudo=True,
        )
        with cd(env.project_dir):
            run("composer install")
            run("chmod -R 777 var/cache var/logs var/sessions")
            run("php bin/console cache:clear")

    fabtools.require.apache.site_disabled('000-default')
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()

    require.apache.site(
        '%s.com' % env.project,
        template_contents=config_tpl,
        port=80,
        hostname=env.site['domain'],
        document_root="%s/web" % env.project_dir,
        )


def install_less():
    require.deb.packages(["nodejs", 'npm'])
    fabtools.files.symlink(source="/usr/bin/nodejs", destination="/usr/bin/node", use_sudo=True)
    sudo("npm install -g less")


def setup():
    sudo("apt-get update")
    sudo("apt-get -y dist-upgrade")
    run("clear")
    install_apache()
    install_php7()
    install_mysql()
    fabtools.service.reload('apache2')
    install_symfony3()
    install_less()

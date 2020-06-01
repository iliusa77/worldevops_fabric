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
env.project = 'roundcube'
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


def install_roundcube():
    sudo("curl -sS https://getcomposer.org/installer | php")
    sudo("mv composer.phar /usr/local/bin/composer")
    sudo("apt-get install -y git")
    with cd(env.home):
        fabtools.git.clone("https://github.com/roundcube/roundcubemail.git", path=env.project)


def configure_apache():
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


def configure_nginx():
    fabtools.require.nginx.disabled('default')
    with open('./nginx/site.conf') as fn:
        config_tpl = fn.read()
    require.nginx.site(env.project,
                       template_contents=config_tpl,
                       port=80,
                       docroot=env.project_dir
                       )
    require.nginx.enabled(env.project)


def credentials():
    print(green("Done"))
    run("clear")
    print(red("Database"))
    print (red("-----------------------------------"))
    print("host:  %s" % env.site['domain'])
    print("login:  %s" % env.db['user'])
    print("pass:  %s" % env.db['pass'])


def config_lighttp():
    with open('./lighttp/php.ini') as fn:
        config = fn.read()
    require.file('/etc/php5/fpm/php.ini', contents=config, use_sudo=True)
    sudo("cp /etc/lighttpd/conf-available/15-fastcgi-php.conf /etc/lighttpd/conf-available/15-fastcgi-php.conf.bak")
    with open('./lighttp/15-fastcgi-php.conf') as fn:
        config = fn.read()
    require.file('/etc/lighttpd/conf-available/15-fastcgi-php.conf', contents=config, use_sudo=True)
    sudo("lighttpd-enable-mod fastcgi")
    sudo("lighttpd-enable-mod fastcgi-php")
    lighttp_config = Path(Path(__file__).ancestor(1), 'lighttp', 'lighttpd.conf')
    destination = Path("/", "etc", "lighttpd")
    upload_template(
        filename=lighttp_config,
        destination=destination,
        context={
            'host_name': env.site['domain'],
            'docroot': env.project_dir,
        },
        use_sudo=True,
    )
    sudo("service lighttpd force-reload")


def config_project_db():
    with cd(env.project_dir):
        run("mv composer.json-dist composer.json")
        run("composer install")
        db_type = "mysql"
        if _mysql_is_installed():
            run("mysql -u%s -p%s %s < SQL/mysql.initial.sql" % (env.db['user'], env.db['pass'], env.db['name']))
        elif _psql_is_installed():
            run("psql %s < SQL/postgres.initial.sql" % env.db['name'])
            db_type = "pgsql"
        elif _sqlite_is_installed():
            run("mysql -u%s -p%s %s < SQL/mysql.initial.sql" % (env.db['user'], env.db['pass'], env.db['name']))
            db_type = "sqlite"
        source = Path(Path(__file__).ancestor(1), 'site', 'config.inc.php')
        destination = Path(env.project_dir, "config")
        fabtools.files.upload_template(
            filename=source,
            destination=destination,
            context={
                'db_type': db_type,
                'db_name': env.db['name'],
                'db_user': env.db['user'],
                'db_pass': env.db['pass'],
            },
            use_sudo=True,
        )
        sudo("rm -rf installer/ SQL/ CHANGELOG INSTALL LICENSE README UPGRADING README.md")


def _mysql_is_installed():
    with settings(hide('stderr'), warn_only=True):
        output = run('mysql --version')
    return output.succeeded


def _psql_is_installed():
    with settings(hide('stderr'), warn_only=True):
        output = run('psql --version')
    return output.succeeded


def _sqlite_is_installed():
    with settings(hide('stderr'), warn_only=True):
        output = run('sqlite --version')
    return output.succeeded


def setup_apache_mysql():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    print(blue('Apache installed'))
    require.deb.packages(["php5", "php5-mysql", "php5-intl", "php5-ldap"])
    print(blue('PHP installed'))
    install_mysql()
    print(blue('MySQL installed'))
    install_roundcube()
    print(blue('Project installed'))
    configure_apache()
    config_project_db()
    credentials()


def setup_apache_pgsql():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    print(blue('Apache installed'))
    require.deb.packages(["php5", "php5-pgsql", "php5-intl", "php5-ldap"])
    print(blue('PHP installed'))
    install_pgsql()
    print(blue('PostgreSQL installed'))
    install_roundcube()
    print(blue('Project installed'))
    configure_apache()
    config_project_db()
    credentials()


def setup_nginx_mysql():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.nginx.server()
    print(blue('Nginx installed'))
    require.deb.packages(["php5-fpm", "php5-mysql", "php5-intl", "php5-ldap", "php5-cli"])
    print(blue('PHP installed'))
    install_mysql()
    print(blue('MySQL installed'))
    install_roundcube()
    print(blue('Project installed'))
    configure_nginx()
    config_project_db()
    credentials()


def setup_nginx_pgsql():
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.nginx.server()
    print(blue('Nginx installed'))
    require.deb.packages(["php5-fpm", "php5-pgsql", "php5-intl", "php5-ldap", "php5-cli"])
    print(blue('PHP installed'))
    install_pgsql()
    print(blue('PostgreSQL installed'))
    install_roundcube()
    print(blue('Project installed'))
    configure_nginx()
    config_project_db()
    credentials()


def setup_lighttpd_mysql():
    sudo("apt-get update && apt-get -y dist-upgrade")
    sudo("apt-get install -y lighttpd")
    print(blue('Lighttp installed'))
    require.deb.packages(["php5-fpm", "php5", "php5-mysql", "php5-cli"])
    print(blue('PHP installed'))
    config_lighttp()
    print (blue("Lighttp Installed"))
    install_mysql()
    print(blue('MySQL installed'))
    install_roundcube()
    print(blue('Project installed'))
    config_project_db()
    sudo("service lighttpd restart")
    credentials()


def setup_lighttpd_pgsql():
    sudo("apt-get update && apt-get -y dist-upgrade")
    sudo("apt-get install -y lighttpd")
    print(blue('Lighttp installed'))
    require.deb.packages(["php5-fpm", "php5", "php5-pgsql", "php5-cli"])
    print(blue('PHP installed'))
    config_lighttp()
    print (blue("Lighttp Installed"))
    install_pgsql()
    print(blue('PostgreSQL installed'))
    install_roundcube()
    print(blue('Project installed'))
    config_project_db()
    sudo("service lighttpd restart")
    credentials()

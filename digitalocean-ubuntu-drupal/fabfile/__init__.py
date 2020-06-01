"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10 setup_nginx

"""
from fabric.api import *
import fabtools
from unipath import Path
from fabric.colors import red
from worldevops import *

env.project = 'drupal'

env.ssh = '/home/%s/.ssh' % env.user
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)

env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': '123123',
    'port': 3306,
    'root': '123123',
    'type': 'mysql',
    'driver': 'pdo_mysql'

}


def install_pgsql():
    fabtools.require.postgres.server()
    fabtools.require.postgres.user(env.db['user'], env.db['pass'])
    fabtools.require.postgres.database(env.db['name'], owner=env.db['user'])
    fabtools.require.service.started('postgresql')


def install_project():
    run("curl https://drupalconsole.com/installer -L -o drupal.phar")
    sudo("mv drupal.phar /usr/local/bin/drupal")
    run("chmod +x /usr/local/bin/drupal")
    run("curl -sS https://getcomposer.org/installer | php")
    sudo("mv composer.phar /usr/local/bin/composer")
    run("drupal site:new --latest drupal")
    with cd(env.project_dir):
        run("composer update")
        command = """drupal site:install standard --langcode=en --db-type={type} --db-host=127.0.0.1 --db-name={name} --db-user={user} --db-pass={pass} --db-port={port} --site-name="Drupal 8 Site Install" --site-mail=admin@example.com --account-name=admin --account-mail=admin@example.com --account-pass=admin -n""".format(**env.db)
        run(command)
    run("chmod -R 0777 %s/sites/default/files" % env.project_dir)


def config_apache():
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()
    fabtools.require.apache.site(
        env.domain,
        template_contents=config_tpl,
        port=80,
        domain=env.domain,
        docroot=env.project_dir
    )


def report():
    run("clear")
    print (red("-----------------------------------"))
    print(red("Congratulations, Drupal has been successfully installed, visit http://%s") % env.domain)
    print(red("lodin - admin"))
    print(red("password - admin"))


def setup():

    sudo("add-apt-repository -y ppa:ondrej/php")
    sudo("apt-get update && apt-get -y dist-upgrade")
    fabtools.require.apache.server()
    sudo("a2enmod rewrite")
    fabtools.require.deb.packages(
        ['php7.0', "php7.0-gd", "php7.0-sqlite", "php7.0-curl",
         "php7.0-xml", "php7.0-mbstring", "git", "unzip"]
    )
    if env.db['driver'] == "pdo_mysql":
        fabtools.require.deb.package("php7.0-mysql")
        install_mysql()
    else:
        fabtools.require.deb.package("php7.0-pgsql")
        env.db['type'] = 'pgsql'
        env.db['port'] = 5432
        install_pgsql()

    install_project()
    config_apache()
    report()

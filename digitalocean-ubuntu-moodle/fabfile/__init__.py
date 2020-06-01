# for Ubuntu 14.04
'''
enter 192.168.33.10 demo.loc in /etc/hosts
how to run: fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.local setup

'''

from fabric.api import *
from fabric.colors import green
import fabtools
from unipath import Path
from fabric.contrib.files import upload_template
from worldevops import *

env.project = 'moodle'
env.home = Path('/home/', env.user)
home_project = Path(env.home, env.project)

env.db = {
    'port': 3306,
    'root': '',
    'name': env.project,
    'user': 'moodle',
    'pass': genpass(),
    'host': 'localhost'
}

env.site = {
	'domain': env.domain,
	'docroot': home_project
}

def common_setup():
	sudo('apt-get update')
	fabtools.require.deb.packages([
		'apache2', 'mysql-client', 'mysql-server', 'php5', 
		'graphviz', 'aspell', 'php5-pspell', 'php5-curl', 
		'php5-gd', 'php5-intl', 'php5-mysql', 'php5-xmlrpc', 
		'php5-ldap', 'git-core',

    ])

def setup_mysql():
	with settings(mysql_user='root', mysql_password=env.db['root']):
		fabtools.require.mysql.user(env.db['user'], env.db['pass'])
		fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root', mysql_password=env.db['root'])
	with settings(mysql_user='root', mysql_password=env.db['root']):
		fabtools.require.mysql.database(env.db['name'], owner=env.db['user'])

def setup_moodle():
	run('mkdir {}'.format(home_project))
	run('mkdir {}/moodledata'.format(home_project))
	with cd(home_project):
		sudo('git clone git://git.moodle.org/moodle.git')
		with cd('{}/moodle'.format(home_project)):
			sudo('git branch -a')
			sudo('git branch --track MOODLE_26_STABLE origin/MOODLE_26_STABLE')
			sudo('git checkout MOODLE_26_STABLE')
	sudo('chmod -R 777 {}/moodle'.format(home_project))
	sudo('chmod -R 777 {}/moodledata'.format(home_project))

def setup_apache():
    fabtools.require.deb.packages(['libapache2-mod-php5'])
    fabtools.require.apache.server()
    fabtools.require.apache.enable_module('rewrite')

    vhost = """
    <VirtualHost *:80>
    ServerName {domain}

    DocumentRoot {docroot}/moodle
    <Directory {docroot}/moodle>
        Options Indexes FollowSymLinks MultiViews
        AllowOverride All
        Require all granted
    </Directory>
    ErrorLog /var/log/apache2/{domain}-error.log
	CustomLog /var/log/apache2/{domain}-access.log combined
</VirtualHost>
        """.format(**env.site)
    fabtools.require.apache.site(config_name='{}'.format(env.domain), template_contents=vhost, enabled=True, check_config=True)
    fabtools.require.service.started('apache2')

def report():
    run("clear")
    print(green("----------------------------------------------------------------------------------------------"))
    print(green("Moodle has been successfully installed, to continue visit http://{}".format(env.domain)))
    print(green("----------------------------------------------------------------------------------------------"))
    print(green("Database info:"))
    print(green("--------------"))
    print('database host: {}'.format(env.db['host']))
    print('database port: {}'.format(env.db['port']))
    print('database name: {}'.format(env.db['name']))
    print('database user: {}'.format(env.db['user']))
    print('database password: {}'.format(env.db['pass']))

def setup():
	common_setup()
	setup_mysql()
	setup_moodle()
	setup_apache()
	report()
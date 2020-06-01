from fabric.api import *
from fabtools import require
import fabtools
import requests
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
from worldevops import *


env.project = 'zabbix'
env.domain = 'zabbix.try.direct'
env.ip = '95.85.25.248'
env.home = Path('/home', '/', env.user)
home_project = Path(env.home, env.project)

env.db = {
    'driver': 'pdo_mysql',
    'host': 'localhost',
    'name': 'zabbix',
    'user': 'zabbix',
    'pass': 'sw9wRd8T',
    'root': '',
    'port': 3306
}

class FabricException(Exception):
    pass

def install_zabbix_server():
	sudo('mkdir {}'.format(home_project))
	with cd(home_project):
		sudo('wget http://repo.zabbix.com/zabbix/3.0/ubuntu/pool/main/z/zabbix/zabbix-frontend-php_3.0.0-1+trusty_all.deb')
		sudo('wget http://repo.zabbix.com/zabbix/3.0/ubuntu/pool/main/z/zabbix/zabbix-server-mysql_3.0.0-1+trusty_amd64.deb')
		with settings(abort_exception=FabricException):
			try:
				sudo('dpkg -i zabbix-frontend-php_3.0.0-1+trusty_all.deb')
			except FabricException:
				sudo('apt-get install -f -y')
				sudo('dpkg -i zabbix-frontend-php_3.0.0-1+trusty_all.deb')
		with settings(abort_exception=FabricException):
			try:
				sudo('dpkg -i zabbix-server-mysql_3.0.0-1+trusty_amd64.deb')
			except FabricException:
				sudo('apt-get install -f -y')
				sudo('dpkg -i zabbix-server-mysql_3.0.0-1+trusty_amd64.deb')

def setup_mysql():
	with settings(mysql_user='root', mysql_password=env.db['root']):
		fabtools.require.mysql.user(env.db['user'], env.db['pass'])
	with settings(mysql_user='root', mysql_password=env.db['root']):
		fabtools.require.mysql.database(env.db['name'], owner=env.db['user'])
	print(env.db['pass'])

def setup_zabbix_server():
    fabtools.require.files.file('/etc/apache2/conf-available/zabbix.conf', source='configs/zabbix.conf', use_sudo=True)
    fabtools.require.files.file('/etc/zabbix/zabbix_server.conf', source='configs/zabbix_server.conf', use_sudo=True)
    with cd('/usr/share/doc/zabbix-server-mysql'):
    	sudo('gzip -d create.sql.gz')
    	sudo('mysql -u {0} -p{1} {2} < create.sql'.format(env.db['user'], env.db['pass'], env.db['name']))

def start_services():
	sudo('service apache2 reload')
	sudo('service zabbix-server start')

def report():
    run("clear")
    print(green("----------------------------------------------------------------------------------------------"))
    print(green("Zabbix 3 has been successfully installed, to continue visit http://{}/zabbix".format(env.domain)))
    print(green("----------------------------------------------------------------------------------------------"))
    print('Admin username: admin')
    print('Admin password: zabbix')
    print(green("--------------"))
    print(green("Database info:"))
    print(green("--------------"))
    print('database host: {}'.format(env.db['host']))
    print('database port: {}'.format(env.db['port']))
    print('database name: {}'.format(env.db['name']))
    print('database user: {}'.format(env.db['user']))
    print('database password: {}'.format(env.db['pass']))


def setup_zabbix_agent():
	with settings(abort_exception=FabricException):
		try:
			sudo('mkdir {}'.format(home_project))
		except FabricException:
			pass
		with cd(home_project):
			sudo('wget http://repo.zabbix.com/zabbix/3.0/ubuntu/pool/main/z/zabbix/zabbix-agent_3.0.0-1+trusty_amd64.deb')
			with settings(abort_exception=FabricException):
				try:
					sudo('dpkg -i zabbix-agent_3.0.0-1+trusty_amd64.deb')
				except FabricException:
					sudo('apt-get install -f -y')
					sudo('dpkg -i zabbix-agent_3.0.0-1+trusty_amd64.deb')
	fabtools.require.files.file('/etc/zabbix/zabbix_agentd.conf', source='configs/zabbix_agentd.conf', use_sudo=True)
	sudo('service zabbix-agent start')

   

def setup():
    sudo('apt-get update')
    with settings(abort_exception=FabricException):
    	try:
    		fabtools.require.deb.packages([
    	'mysql-server', 'mysql-client', 'apache2', 'php5', 'php5-mysql', 'php5-pgsql', 'php5-gd', 'php5-ldap', 'ttf-dejavu-core', 'ttf-japanese-gothic'
    	])
    	except FabricException:
    		sudo('apt-get install -f -y')
    		fabtools.require.deb.packages([
    	'mysql-server', 'mysql-client', 'apache2', 'php5-mysql', 'php5-pgsql', 'php5-gd', 'php5-ldap', 'ttf-dejavu-core', 'ttf-japanese-gothic'
    	])
    install_zabbix_server()
    setup_mysql()
    setup_zabbix_server()
    start_services()
    report()

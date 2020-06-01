"""

how to run:  fab -H 192.168.33.10 --user vagrant --password vagrant setup


"""
from unipath import Path
from fabric.colors import green, red
from worldevops import *

env.project = 'egroupware33'
commonname = 'egroupware33.com'
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)

env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': genpass(),
    'port': 3306,
    'root': genpass(),
}


def config_apache():
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()
    fabtools.require.apache.site(
        commonname,
        template_contents=config_tpl,
        port=80,
        domain=commonname,
        docroot='{}/egroupware'.format(env.project_dir)
    )

def install_egroupware():
    run('mkdir {}'.format(env.project_dir))
    with cd(env.project_dir):
        run('wget "http://jpgraph.net/download/download.php?p=5" -O ./jpgraph.tar.gz')
        run('tar -zxf jpgraph.tar.gz')
        run('rm -f jpgraph.tar.gz')
        run('mv jpgraph* jpgraph')
        run('wget https://github.com/EGroupware/egroupware/releases/download/16.1.20160801/egroupware-epl-16.1.20160801.tar.gz')
        run('tar zxf egroupware-epl-16.1.20160801.tar.gz -C {} && rm -f egroupware-epl-16.1.20160801.tar.gz'.format(env.project_dir))
    #for postinstallation
    run('mkdir {0}/backup && chmod a+w {0}/backup'.format(env.project_dir))
    sudo('mkdir -p /var/lib/default/files && chmod a+w /var/lib/default/files')


def report():
    run("clear")
    print (green("-----------------------------------"))
    print(green("Congratulations, Egroupware has been successfully installed, for final installation visit http://%s") % commonname)
    print('\n')
    print(green('MYSQL database'))
    print(green('------------------------------------'))
    print('Host: %s' % env.db['host'])
    print('Database name: %s' % env.db['name'])
    print('Database user: %s' % env.db['user'])
    print('Database user password: %s' % env.db['pass'])
    print('\n')
    print(red('Info for Postinstallation'))
    print(red('------------------------------------'))
    print('for "Step 2 - configuration" of "Setup - Domain" created writable folder: /var/lib/default/files')
    print('for "Step 2 - configuration" of "Setup - Domain" created writable folder: {0}/backup'.format(env.project_dir))
    print('\n')
    print(red('Steps of Postinstallation'))
    print(red('------------------------------------'))
    print(red('0 - Press "Run installation tests"'))
    print(red('1 - Down press "Continue to the Header Admin"'))
    print(red('2 - Fill fields in "Header", "Database instance", press "View" and copy content in file {}/egroupware/header.inc.php'.format(env.project_dir)))
    print(red('3 - Press "Continue"'))
    print(red('4 - In "Setup/config admin login" enter login and password and press "Login"'))
    print(red('5 - In "Step 1 - simple application management" of "Setup - Domain" press "Install"'))
    print(red('6 - In "Step 1 - simple application management" of "Setup - Domain" press "Re-check my installation"'))
    print(red('7 - In "Step 2 - configuration" of "Setup - Domain" press "Edit current configuration"'))
    print(red('8 - Fill fields with /var/lib/default/files, {0}/backup and press "Save"'.format(env.project_dir)))
    print(red('9 - In "Step 3 - admin account" of "Setup - Domain" press "Create admin account"'))
    print(red('10 - Fill fields, check "Give admin access to all installed apps", "Create demo accounts" and press "Save"'))
    print(red('11 - Press "Clear cache and register hooks" and down press "Save"'))
    print(red('12 - Press "Back to user login" and enter in Egroupware'))

def setup():
    sudo("apt-get update")
    fabtools.require.deb.packages(['php5', 'php5-gd', 'php5-imap', 'php5-ldap', 'php5-mysql', 'php-pear', 'tnef'])
    fabtools.require.apache.server()
    sudo("php5enmod imap")
    sudo('sed -E -i "s/(upload_max_filesize.*=)(.*)/\1 8M/" /etc/php5/apache2/php.ini')
    sudo('sed -E -i "s/(^.*date.timezone.*=)/date.timezone = America\/New_York/" /etc/php5/apache2/php.ini')
    sudo('sed -E -i "s/^.*mbstring.func_overload.*/mbstring.func_overload = 0/" /etc/php5/apache2/php.ini')
    sudo("service apache2 restart")
    install_mysql()
    config_apache()
    install_egroupware()
    report()





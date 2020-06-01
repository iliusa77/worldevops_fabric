from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green


class FabricException(Exception):
    pass


def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))


env.hosts = [
    'mybitrix24.com',
]

env.site = {
    'domain': 'mybitrix24.com',
}

env.user = 'vagrant'
env.password = 'vagrant'
env.project = 'bitrix24'

env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': genpass(),
    'port': 3306,
    'root': genpass()
}

env.ssh = '/home/%s/.ssh' % env.user

#Corporate Portal ru
#link = 'http://www.1c-bitrix.ru/download/intranet_business_encode_php5.tar.gz'
#Holding ru
#link = 'http://www.1c-bitrix.ru/download/intranet_holding_encode_php5.tar.gz'
#Bitrix24 BizPace 30-Day Trial en
link = 'http://www.bitrixsoft.com/download/portal/intranet_bizspace_encode_php5.tar.gz'
env.project_path = Path('/', 'home', env.user, env.project)


def setup_db():
    require.mysql.server(password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        query = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (env.db['user'], env.db['pass'])
        fabtools.mysql.query(query=query, use_sudo=True)
    fabtools.mysql.query('DROP DATABASE IF EXISTS `%s`' % env.db['name'], use_sudo=True, mysql_user='root',
                         mysql_password=env.db['root'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        require.mysql.database(env.db['name'], owner=env.db['user'])
    require.deb.package("php5-mysql")


def setup_domain():
    stype = 'apache'
    if stype == 'nginx':
        require.nginx.site(env.project,
                           template_source='./nginx/production.conf',
                           domain=env.site['domain'],
                           docroot=env.project_path
                           )
        require.service.start('nginx')
    if stype == 'apache':
        require.apache.site(env.project,
                            template_source='./apache/site.conf',
                            domain=env.site['domain'],
                            docroot=env.project_path,
                            home=env.project_path
                            )
        require.service.start('apache2')
        source = Path('./', 'apache', 'htaccess')
        target = Path(env.project_path, '.htaccess')
        upload_template(source, target, use_sudo=True)


def config():
    source = Path('./', 'php', 'php.ini')
    target = Path("/", 'etc', 'php5', 'apache2', 'php.ini')
    upload_template(source, target, use_sudo=True)
    sudo("service apache2 restart")


def chmod():
    with cd("~"):
        sudo("chmod -R 0777 %s" % env.project)


def setup():
    #sudo("apt-get update && apt-get -y dist-upgrade")
    sudo("apt-get update")
    fabtools.require.apache.server()
    setup_db()
    require.deb.packages(['php5', "php5-gd", "php5-mcrypt"])
    sudo("php5enmod mcrypt")
    if fabtools.files.is_dir(env.project_path):
        sudo('rm -r ' + env.project_path)
    run('mkdir -p ' + env.project_path)
    with cd(env.project_path):
        if not fabtools.files.is_file('source.tar.gz'):
            run("wget -O source.tar.gz %s" % link)
            print(green('Source downloaded'))
        run('tar xvzf source.tar.gz')
        print(green('Source unzipped'))
    setup_domain()
    config()
    chmod()
    credentials()


def credentials():
    print(green('You can access your site by URL http://%s/' % env.site['domain']))
    print(green('------------------------------------'))
    print('\n')
    print(green('MYSQL database'))
    print(green('------------------------------------'))
    print('Host: %s' % env.db['host'])
    print('Database name: %s' % env.db['name'])
    print('Database user: %s' % env.db['user'])
    print('Database user password: %s' % env.db['pass'])
    print('\n')

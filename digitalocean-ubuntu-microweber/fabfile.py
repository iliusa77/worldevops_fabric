from unipath import Path
from fabric.contrib.files import upload_template
from worldevops import *
from fabtools import require
from fabric.colors import green
from fabric.colors import red

env.project = 'mymicroweber'
commonname = 'mymicroweber.com'
env.home = Path('/', 'home', env.user)
env.project_dir = Path(env.home, env.project)

env.db = {
    'host': 'localhost',
    'name': env.project,
    'user': env.user,
    'pass': genpass(),
    'port': 3306,
    'root': ''
}

env.site = {
    'domain': commonname,  # without www.
    'docroot': env.project_dir,
    'ssl': True,
    'certfile': '/etc/nginx/ssl/{}'.format(env.project),
    'keyfile': '/etc/nginx/ssl/{}'.format(env.project),
    'user': env.user,
}

#Change to client company details
env.reqdata = {
    'country': 'GB',
    'state': 'Nottingham',
    'locality': 'Nottinghamshire',
    'organization': '{}'.format(commonname),
    'commonname': commonname,
    'domain': env.project
}

env.php_fpm = {
    'user': env.user,
    'group': env.user,
    'listen': env.user,
    'listen.owner': env.user,
    'listen.group': env.user
}


def install_microweber():
    sudo('mkdir -p {}'.format(env.project_dir))
    with cd(env.project_dir):
        sudo('git clone https://github.com/microweber/microweber.git .')
        sudo('composer install')
        sudo('php artisan microweber:install %(user)s@%(name)s %(user)s %(pass)s 127.0.0.1 %(name)s %(user)s %(pass)s' % env.db)

def genssl():
    sudo('mkdir -p /etc/nginx/ssl')
    with cd('/etc/nginx/ssl'):
        sudo('openssl genrsa -des3 -passout pass:x -out {}.pass.key 2048'.format(env.project))
        sudo('openssl rsa -passin pass:x -in {0}.pass.key -out {0}.key'.format(env.project))
        sudo('rm {}.pass.key'.format(env.project))
        sudo('openssl req -new -key %(domain)s.key -out %(domain)s.csr \
        -subj "/C=%(country)s/ST=%(state)s/L=%(locality)s/O=%(organization)s/CN=%(commonname)s"' % env.reqdata)
        sudo('openssl x509 -req -days 365 -in {0}.csr -signkey {0}.key -out {0}.crt'.format(env.project))


def php_fpm_setup():
    upload_template(
        filename=Path('./', 'php-fpm', 'user.conf'),
        destination='/etc/php5/fpm/pool.d/{}.conf'.format(env.user),
        context=env.php_fpm, use_sudo=True
    )
    fabtools.service.reload('php5-fpm')

def setup_nginx():
    fabtools.require.nginx.server()
    if env.site['ssl'] == True:
        upload_template(
            filename=Path('./', 'nginx', 'ssl-site.conf'),
            destination='/etc/nginx/sites-available/ssl-{}.conf'.format(env.project),
            context=env.site, use_sudo=True
        )
        sudo("ln -s /etc/nginx/sites-available/ssl-{0}.conf /etc/nginx/sites-enabled/ssl-{0}.conf".format(env.project))
    else:
        upload_template(
            filename=Path('./', 'nginx', 'site.conf'),
            destination='/etc/nginx/sites-available/{}.conf'.format(env.project),
            context=env.site, use_sudo=True
        )
        sudo("ln -s /etc/nginx/sites-available/{0}.conf /etc/nginx/sites-enabled/{0}.conf".format(env.project))
    fabtools.service.reload('nginx')

def credentials():
    print(green('You can access your site by URL http://%s/' % env.site['domain']))
    print(green('---------------------------------------------------------------'))
    print('\n')
    print(red('You have admin access your site by URL http://%s/admin' % env.site['domain']))
    print(green('-------------------------------------------------------------------------'))
    print('Admin username: %s' % env.db['user'])
    print('Admin password: %s' % env.db['pass'])
    print('\n')
    print(green('MYSQL database'))
    print(green('------------------------------------'))
    print('Host: %s' % env.db['host'])
    print('Database name: %s' % env.db['name'])
    print('Database user: %s' % env.db['user'])
    print('Database user password: %s' % env.db['pass'])
    print('\n')

def setup():
    sudo('apt-get update && sudo apt-get -y upgrade')
    sudo('add-apt-repository -y ppa:ondrej/php5-5.6')
    sudo('apt-get update')
    require.deb.packages([
        'software-properties-common', 'git', 'curl', 'mysql-server',
        'php5-fpm', 'php5-cli', 'php5-json', 'php5-curl', 'php5-gd',
        'php5-mysqlnd', 'php5-imap', 'php5-mcrypt',
    ])
    run('curl -sS https://getcomposer.org/installer | php')
    sudo('mv composer.phar /usr/local/bin/composer')
    install_mysql()
    install_microweber()
    genssl()
    php_fpm_setup()
    setup_nginx()
    sudo('chown -R {0}.{0} {1}'.format(env.user, env.project_dir))
    credentials()

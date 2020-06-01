"""
Example command:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc setup
"""
import fabtools
from fabric.api import *
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
import sys

# root = Path(os.path.abspath('../'))
root = Path(__file__).ancestor(2)
sys.path.append(root)
from worldevops import *


env.project = 'sylius'
production = True  # false - will install development version

env.db = {
    'driver': 'pdo_mysql',
    'host': 'localhost',
    'name': env.project,
    'user': env.project,
    'pass': genpass(),
    'port': 3306,
    'root': genpass()
}

env.app = {
    'secret': gensecret(),
    'phpcruser': 'phpcruser',
    'phpcruserpwd': 'phpcruserpwd',
    'open_exchange_rates': 'exchange',
    'amazonid': 'amazonid',
    'amazonsecret': 'amazonsecret',
    'fbid': 'fbid',
    'fbsecret': 'fbsecret',
    'googleid': 'googleid',
    'googlesecret': 'googlesecret',
}

home = Path('/', 'home', env.user)
path = Path(home, 'projects',  env.project)


def _composer_is_installed():
    with settings(hide('stderr'), warn_only=True):
        out = run('composer --version')
    return out.succeeded


def setup_composer():
    """@setup composer"""
    if not _composer_is_installed():
        run('curl -sS https://getcomposer.org/installer | php')
        sudo('mv composer.phar /usr/local/bin/composer')
        print(green('Composer installed'))
    else:
        print(green('Composer already installed'))


def upload_config():
    upload_template(
        './config/parameters.yml',
        Path(path, 'app', 'config'),
        use_sudo=True,
        context={'db_host': env.db['host'], 'db_port': env.db['port'], 'db_name': env.db['name'],
                 'db_user': env.db['user'], 'db_password': env.db['pass'], 'db_driver': env.db['driver'],
                 'secret': env.app['secret'], 'phpcr_userpwd': env.app['phpcruserpwd'],
                 'phpcr_user': env.app['phpcruser'], 'open_exchange_rates': env.app['open_exchange_rates'],
                 'amazon_id': env.app['amazonid'], 'amazon_secret': env.app['amazonsecret'],
                 'fb_id': env.app['fbid'], 'fb_secret': env.app['fbsecret'],
                 'google_id': env.app['googleid'], 'google_secret': env.app['googlesecret'],
                 }
    )
    put('./php/php-fpm.ini', '/etc/php5/fpm/php.ini', use_sudo=True)
    fabtools.service.stop('php5-fpm')
    fabtools.service.start('php5-fpm')
    print(green('Config uploaded'))


def setup_app_db():
    sudo('mysqldump --user="%s" --password="%s" %s > %s/dump.sql' % (
            'root', env.db['root'], env.db['name'] + '_dev', path
        )
    )
    sudo('mysql --user="%s" --password="%s" %s < %s/dump.sql' % ('root', env.db['root'], env.db['name'], path))


def setup_http():
    fabtools.require.nginx.site(env.project, template_source='./nginx/sylius.conf', domain=env.domain)


def chmod():
    with cd(path):
        # no need because of shared memory usage
        # sudo('chmod 777 -R app/logs/')
        # sudo('chmod 777 -R app/cache/')
        sudo('chmod 777 -R web/')
        sudo('chmod a+w app/config/parameters.yml')


def chown():
    with cd(path):
        sudo('chown {user}:{user} {dir}'.format(user=env.user, dir=path))
        sudo('gpasswd -a www-data {}'.format(env.user))


def remove():
    with cd(path):
        sudo('rm -rf ./install')


def destroy():
    sudo('rm -rf {}'.format(path))
    destroy_mysql()


def setup_app():

    sudo('rm -rf {}'.format(path))
    run('mkdir -p ' + path)

    with cd(path):
        # ccache = str(Path(home, '.composer'))
        # sudo('rm -rf ' + ccache)  # clear composer cache
        # if not fabtools.files.is_dir(ccache):
        #     run('mkdir {}'.format(ccache))

        # because composer tryes to access  (/dev/shm/sylius/cache/dev) for cache we use sudo here
        run('composer clearcache')
        if production:
            run('composer create-project -s stable sylius/sylius-standard .')
        else:
            run('composer -n create-project sylius/sylius -s dev .')

        upload_config()
        chmod()
        run('php app/console sylius:install')
        setup_app_db()
        chmod()
        chown()
        run('php app/console cache:clear')


def app():
    with cd(path):
        run('php app/console cache:clear')
        run('php app/console sylius:install')

def setup():
    # shared memory
    sudo('mkdir -p {}'.format('/dev/shm/sylius'))
    sudo('chown -R {user}:{user} {dir}'.format(user=env.user, dir='/dev/shm/sylius'))
    fabtools.require.nginx.server()
    fabtools.require.mysql.server(password=env.db['root'])
    fabtools.require.deb.packages([
        'php5-fpm',
        'php5-cli',
        'libxml2-dev',
        'php5-json',
        'php5-mysql',
        'php5-gd',
        'php5-curl',
        'php5-intl',
        'php-apc',
        'git',
        'tar',
        'unzip'
    ])
    setup_composer()
    install_mysql()
    setup_http()
    setup_wkhtml2pdf()
    setup_app()
    restart_services()
    print(green('Done'))
    run('clear')
    report()


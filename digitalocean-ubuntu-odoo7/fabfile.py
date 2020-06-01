'''

fab -H 192.168.33.11 --user vagrant --password vagrant setup

'''

from fabric.api import *
from fabric.contrib.files import upload_template
from fabtools import require
import fabtools
from unipath import Path
from fabric.colors import *


env.odoo_user = 'openerp'
env.odoo_user_pwd = 'openerp'

env.site = {
    'domain': 'example.com',  # without www.
    'docroot': Path('/', 'home', 'openerp'),
    'ssl': False
}

env.remote_dir = Path('/', 'opt', 'openerp')

env.db = {
    'driver': 'pdo_pgsql',
    'host': 'localhost',
    'name': 'demonstration',
    'user': 'openerp',
    'pass': 'openerp',
    'port': 8532
}


class FabricException(Exception):
    pass


@task
def create_app_user(user, passwd):
    print('Create master: {0} with password: {1} at {2}'.format(user, passwd, env.host_string))
    fabtools.require.user(user, password=passwd, create_home=True)
    fabtools.require.users.sudoer(user, hosts='ALL', operators='ALL', passwd=False, commands='ALL')


@task
def simple_setup():
    sudo('wget -O - https://nightly.odoo.com/odoo.key | apt-key add -')
    sudo('echo "deb http://nightly.odoo.com/7.0/nightly/deb/ ./" >> /etc/apt/sources.list')
    sudo('mkdir -p /var/lib/openerp')
    sudo('apt-get update && apt-get install openerp -y')


@task
def restart_services():
    with settings(abort_exception=FabricException):
        try:
            fabtools.service.stop('openerp')
        except FabricException:
            sudo('killall openerp')

    sudo("service nginx reload")
    sudo("service nginx restart")
    fabtools.require.service.started('openerp')
    #sudo('/etc/init.d/odoo-server restart')


@task
def setup_user():
    require.user(name=env.user, comment='This user is used for setup application',
                 create_home=True)
    fabtools.user.add_ssh_public_key(env.user, '~/.ssh/id_rsa.pub')


def setup_firewall():
    sudo('ufw allow ssh')
    sudo('ufw allow 8069/tcp')
    sudo('ufw enable')


def setup_nginx():
    sudo('rm -f /etc/nginx/sites-enable/site.conf')
    sudo('rm -f /etc/nginx/sites-available/site.conf')
    if env.site['ssl'] == True:
        upload_template(
            filename=Path('./', 'etc', 'nginx', 'ssl-site.conf'),
            destination='/etc/nginx/sites-available/site.conf',
            context=env.site, use_sudo=True
        )
    else:
        upload_template(
            filename=Path('./', 'etc', 'nginx', 'site.conf'),
            destination='/etc/nginx/sites-available/site.conf',
            context=env.site, use_sudo=True
        )

    sudo('rm -f /etc/nginx/sites-enabled/site.conf')
    sudo("ln -s /etc/nginx/sites-available/site.conf /etc/nginx/sites-enabled/site.conf")


@task
def setup():
    # Require some Debian/Ubuntu packages
    # sudo('apt-get update && apt-get -y dist-upgrade')

    require.deb.packages([
        'imagemagick', 'libxml2-dev', 'libxml2',
        'libxslt1.1', 'libevent-2.0-5', 'libsasl2-2',
        'libldap-2.4-2', 'python-dev', 'libjpeg-dev',
        'libpcre3', 'libpcre3-dev', 'nginx','supervisor',
        'python-pip', 'python-virtualenv', 'python-docutils', 
        'python-gdata', 'python-mako', 'python-dateutil', 'python-lxml',
        'python-libxslt1', 'python-libxslt1', 'python-reportlab', 'python-pybabel',
        'python-pychart', 'python-openid', 'python-simplejson', 'python-psycopg2',
        'python-vobject', 'python-vatnumber', 'python-webdav', 'python-xlwt',
        'python-yaml', 'python-zsi',
        'gunicorn', 'fabric', 'python-unipath', 'npm', 'git', 'ufw',
        'libxml2-dev', 'libxslt1-dev', 'zlib1g-dev',
        'libsasl2-dev', 'libldap2-dev', 'libssl-dev',
        'node-less'
    ])

    sudo('apt-get -y autoremove')
    sudo('pip install --upgrade pip')

    # setup wkhtml2pdf
    with cd('/tmp'):
        sudo('wget http://download.gna.org/wkhtmltopdf/0.12/0.12.1/wkhtmltox-0.12.1_linux-trusty-amd64.deb')
        sudo('dpkg -i wkhtmltox-0.12.1_linux-trusty-amd64.deb')
        sudo('cp /usr/local/bin/wkhtmltopdf /usr/bin')
        sudo('cp /usr/local/bin/wkhtmltoimage /usr/bin')

    # Require a PostgreSQL server

    with settings(abort_exception=FabricException):
        try:
            fabtools.require.deb.packages(['postgresql-server-dev-all', 'postgresql-client', 'python-psycopg2'])
        except FabricException:
            sudo('apt-get -f -y install')

    with settings(abort_exception=FabricException):
        try:
            require.postgres.server()
        except FabricException:
            with cd ('/var/lib/dpkg/info'):
                sudo('rm postgresql-server.*')
            sudo('apt-get -f -y install')

    require.postgres.user(env.db['user'], env.db['pass'], createdb=True)
    require.postgres.database(env.db['name'], env.db['user'])  # setup firewall
    # setup_firewall()
    require.user(env.odoo_user, password=env.odoo_user_pwd)

    with settings(abort_exception=FabricException):
        try:
            sudo('mkdir /opt')
        except FabricException:
            pass

    sudo('chmod g+w /opt')

    with cd('/opt'):
        sudo('rm -rf ./openerp')
        sudo('rm -rf ./openerp/.git')
        with settings(abort_exception=FabricException):
            try:
                sudo('mkdir openerp')
                sudo('chown openerp.openerp ./openerp')
                sudo('chmod g+w ./openerp')
            except FabricException:
                pass

    sudo('wget -O - https://nightly.odoo.com/odoo.key | apt-key add -')
    sudo('echo "deb http://nightly.odoo.com/7.0/nightly/deb/ ./" >> /etc/apt/sources.list')
    sudo('mkdir -p /var/lib/openerp')
    sudo('apt-get update && apt-get install openerp -y')

    #with cd(env.remote_dir):
    #    sudo('git clone https://www.github.com/odoo/odoo --depth 1 --branch 7.0 --single-branch .')
    #    with settings(abort_exception=FabricException):
    #        try:
    #            sudo('pip install')
    #        except FabricException:
    #            sudo('apt-get install -f -y')
    #            sudo('pip install')
    #
    #    sudo('npm install -g less less-plugin-clean-css')
    #    with settings(abort_exception=FabricException):
    #        try:
    #            sudo('ln -s /usr/bin/nodejs /usr/bin/node')
    #        except FabricException:
    #            pass

    upload_template(
        filename='./etc/openerp-server.conf',
        destination='/etc/openerp/openerp-server.conf',
        context=env.db, use_sudo=True
    )
    put('./etc/init.d/openerp', '/etc/init.d/openerp', use_sudo=True)

    setup_nginx()

    # Correct ownership and permissions
    sudo('chmod 755 /etc/init.d/openerp')
    sudo('chown root: /etc/init.d/openerp')
    # Since odoo user will run the application, change its ownership accordingly.

    sudo('chown -R openerp: /opt/openerp/')
    # We should set odoo user as the owner of log directory as well.

    #with settings(abort_exception=FabricException):
    #    try:
    #        sudo('mkdir /var/log/openerp')
    #    except FabricException:
    #        pass

    sudo('chown openerp:root /var/log/openerp')
    # Finally, we should protect the server configuration file changing
    # its ownership and permissions so no other non-root user can access it.


    # @todo this small part isn't working yet, try manual -./openerp-server -u all -d DATABASENAME
    # using odoo user
    with cd(env.remote_dir):
        #sudo('su odoo && ./openerp-server -u all -d %s' % env.db['name'], user=env.odoo_user)
        pass

    sudo('chown openerp: /etc/openerp/openerp-server.conf')
    sudo('chown root: /etc/nginx/sites-available/site.conf')
    sudo('chmod 640 /etc/openerp/openerp-server.conf')

    report()
    restart_services()
    print(green('Installation complete. Please visit http://<ip address>:8069'))
    autostart()
    # Setup a daily cron task  # fabtools.cron.add_daily('maintenance', 'myuser', 'my_script.py')


@task
def test():
    sudo('/etc/init.d/openerp start')
    sudo('cat /var/log/openerp/openerp-server.log')


@task
def setup_with_docker():
    sudo('docker run -d -e POSTGRES_USER=openerp -e POSTGRES_PASSWORD=openerp --name db postgres')
    sudo('docker run -p 8069:8069 --name openerp --link db:db -t openerp')
    sudo('docker stop openerp')
    sudo('docker start openerp')


#def autostart():
#    sudo('update-rc.d openerp defaults')


@task
def report():
    report = []
    report.append("""
    """ % {'domain': env.site['domain']})

    report.append("\n" + 20 * '=' + ' Site ' + 20 * '=')
    dbs = []
    for k, v in env.site.items():
        dbs.append(str(k) + ': ' + str(v))
    report.append("\n".join(dbs))

    report.append("\n" + 20 * '=' + ' Database ' + 20 * '=')
    report.append(env.db['driver'])
    dbs = []
    for k, v in env.db.items():
        dbs.append(str(k) + ': ' + str(v))
    report.append("\n".join(dbs))

    if 'cache_server' in env:
        report.append("\n" + 20 * '=' + ' Cache server ' + 20 * '=')
        report.append(env.cache_server)
        dbs = []
        for k, v in env.redis.items():
            dbs.append(str(k) + ': ' + str(v))
        report.append("\n".join(dbs))
    print("\n".join(report))

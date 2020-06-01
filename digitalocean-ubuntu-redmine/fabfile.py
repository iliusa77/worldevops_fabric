"""
Command sequence for testing in vagrant:

fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10 create_app_user:redmine,redmine
fab -H demo.loc --user redmine --password redmine --set=domain=demo.loc,ip=192.168.33.10 setup

"""
import os
from fabric.api import task, run, env, settings, cd, sudo, prefix, put
from fabric.contrib.files import upload_template
import fabtools
from fabric.contrib import files
from contextlib import contextmanager
from unipath import Path


def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))


class FabricException(Exception):
    pass

env.with_mail = True
env.use_ssh_config = True
env.project = 'redmine'
env.activate = 'source ~/ruby-env'
env.local_root = Path(__file__).ancestor(1)


env.site = {
    'domain': env.domain,
    'ssl': False,
    'ip': env.ip,
    'port': 80
}

env.http_server = 'apache'
env.redmine = {'public': '/home/{user}/redmine/public'.format(user=env.user)}

env.redmine = {
    'public': '/home/{user}/redmine/public'.format(user=env.user),
    # 'version': 'trunk'
    #'version': 'http://www.redmine.org/releases/redmine-3.2.1.tar.gz'
    'version': 'http://www.redmine.org/releases/redmine-3.3.0.tar.gz'
}

env.db = {
    'driver': 'mysql',
    'root': os.environ.get('MYSQL_PASSWORD', genpass()),
    'name': env.project,
    'user': env.project,
    'pass': genpass(),
    'host': 'localhost',
}

#  PostgreSQL
env.db['driver'] = 'pgsql'  # you can choose from mysql|postgresql|sqlite
env.db['port'] = 5432
env.db['url'] = 'postgres://%(user)s:%(pass)s@%(host)s:%(port)d/%(name)s' % env.db

#  MySQL
# env.db['port'] = 3306
# env.db['url'] = 'mysql://%(user)s:%(pass)s@%(host)s:%(port)d/%(name)s' % env.db
# env.db_str = ''  # db setting string for django settings.py file

@task
def create_app_user(user, passwd):
    print('Create application user {0} with password {1} at {2}'.format(user, passwd, env.domain))
    fabtools.require.user(user, password=passwd, create_home=True)
    fabtools.require.users.sudoer(user, hosts='ALL', operators='ALL', passwd=False, commands='ALL')


@contextmanager
def source_virtualenv():
    with prefix(env.activate):
        yield


@task
def upgrade():
    fabtools.deb.update_index()
    fabtools.deb.upgrade()

@task
def setup_mail():
    if env.with_mail == True:
        sudo('apt-get install -y sendmail')
        with cd('/home/{user}/redmine/'.format(user=env.user)):
            fabtools.require.file('/home/redmine/redmine/config/configuration.yml', """\
default:
 production:
  email_delivery:
    delivery_method: :async_sendmail
 attachments_storage_path:
 autologin_cookie_name:
 autologin_cookie_path:
 autologin_cookie_secure:
 scm_subversion_command:
 scm_mercurial_command:
 scm_git_command:
 scm_cvs_command:
 scm_bazaar_command:
 scm_darcs_command:
 scm_subversion_path_regexp:
 scm_mercurial_path_regexp:
 scm_git_path_regexp:
 scm_cvs_path_regexp:
 scm_bazaar_path_regexp:
 scm_darcs_path_regexp:
 scm_filesystem_path_regexp:
 scm_stderr_log_file:
 database_cipher_key:
 rmagick_font_path:
production:
development:
 """)
            sudo('service supervisor restart')



@task
def setup():
    fabtools.require.deb.packages(['sudo'])
    fabtools.require.system.locale('en_US.UTF-8')
    fabtools.deb.update_index()

    fabtools.require.deb.packages([
        'build-essential',
        'devscripts',
        'locales',
        'vim',
        'mc',
        'curl',
        'wget',
        'ruby2.0',
        'ruby2.0-dev',
        'supervisor',
        'python-pip',
        'python-dev',
        'subversion',
        'libxslt1-dev',
        'libxml2-dev',
        'libmysqld-dev',
        'libmagick++-dev',
        'libsqlite3-dev',
        'libgmp-dev'
    ])
    sudo('apt-get -y autoremove')
    sudo('update-alternatives --install /usr/bin/ruby ruby /usr/bin/ruby2.0 10')
    sudo('update-alternatives --install /usr/bin/gem gem /usr/bin/gem2.0 10')

    setup_db_server()

    run('mkdir -p /home/{}/gem'.format(env.user))
    fabtools.require.file('/home/{}/ruby-env'.format(env.user), contents="""\
export GEM_HOME=~/gem
export RUBYLIB=~/lib
export PATH=~/bin:$GEM_HOME/bin:$PATH
export RAILS_ENV=production
""", use_sudo=True)
    files.append('/home/{}/.profile'.format(env.user), 'source ~/ruby-env')
    run('rm -rf redmine')
    run('rm -rf redmine-*')
    run('wget http://production.cf.rubygems.org/rubygems/rubygems-2.6.4.tgz')
    run('tar xzf rubygems-2.6.4.tgz')
    run('cd rubygems-2.6.4; ruby setup.rb --prefix=~ --no-format-executable')
    run('rm -rf rubygems*')

    with source_virtualenv():
        run('gem install bundler')
        run('gem install rmagick')

    if env.redmine['version'] == 'trunk':
        run('svn co http://svn.redmine.org/redmine/trunk redmine-trunk')
        run('mv redmine-trunk redmine')
    else:
        run('wget %s' % env.redmine['version'])
        run('tar xzf redmine-*')
        run('rm -f *.tar.gz')
        run('mv redmine-* redmine')

    setup_db_config()

    with cd('/home/{user}/redmine/'.format(user=env.user)):
        fabtools.require.file('/home/redmine/redmine/config/thin.conf', """\
daemonize: false
chdir: /home/redmine/redmine
pid: tmp/pids/thin.pid
log: log/thin.log
prefix: /
environment: production
 """)
        run('chmod 0600 config/database.yml')
        files.append('/home/redmine/redmine/Gemfile', 'gem "thin"')

        with source_virtualenv():
            run('bundle install --without sqlite postgresql')
            run('rake generate_secret_token')
            run('rake db:migrate')
            run('rake redmine:load_default_data REDMINE_LANG=en')

        fabtools.require.file('/etc/supervisor/conf.d/redmine.conf', """\
[program:redmine]
process_name=%(program_name)s_%(process_num)02d
directory=/home/redmine/redmine/
user=redmine
numprocs=2
autostart=true
autorestart=true
startsecs=10
redirect_stderr=true
stdout_logfile=/var/log/supervisor/redmine-thin.log
command=/home/redmine/gem/bin/thin -C config/thin.conf -p 30%(process_num)02d start
environment=GEM_HOME='/home/redmine/gem',RUBYLIB='/home/redmine/lib',RAILS_ENV='production'""", use_sudo=True)

    sudo('supervisorctl reload')

    setup_http_server()
    setup_mail()
    report()


def setup_db_server():

    if env.db['driver'] == 'mysql':
        # fabtools.deb.preseed_package('mysql-server', {
        #     'mysql-server/root_password': ('password', env.db['root']),
        #     'mysql-server/root_password_again': ('password', env.db['root']),
        # })

        fabtools.require.deb.packages(['python-mysqldb', 'libmysqlclient-dev'])
        fabtools.require.mysql.server(password=env.db['root'])
        with settings(mysql_user='root', mysql_password=env.db['root']):
            fabtools.require.mysql.user(env.db['user'], env.db['pass'])
        with settings(mysql_user='root', mysql_password=env.db['root']):
            fabtools.require.mysql.database(env.db['name'], owner=env.db['user'])
        fabtools.require.service.started('mysql')

    if env.db['driver'] == 'pgsql':
        fabtools.require.postgres.server()
        fabtools.require.deb.packages(['postgresql-server-dev-9.3', 'postgresql-client', 'python-psycopg2'])
        fabtools.require.postgres.user(env.db['user'], env.db['pass'])
        fabtools.require.postgres.database(env.db['name'], owner=env.db['user'])
        fabtools.require.service.started('postgresql')


def setup_db_config():
    if env.db['driver'] == 'mysql':
        setup_mysql_config()
    if env.db['driver'] == 'pgsql':
        setup_pgsql_config()


def setup_mysql_config():
    with cd('/home/{user}/redmine/'.format(user=env.user)):
        fabtools.require.file('/home/redmine/redmine/config/database.yml', """\
production:
    adapter: mysql2
    database: redmine
    host: localhost
    socket: /var/run/mysqld/mysqld.sock
    username: redmine
    password: %s
    encoding: utf8
    reconnect: true

test:
    adapter: sqlite3
    database: db/redmine.db
""" % env.db['pass'])


def setup_pgsql_config():
    with cd('/home/{user}/redmine/'.format(user=env.user)):
        fabtools.require.file('/home/redmine/redmine/config/database.yml', """\
production:
    adapter: postgresql
    database: redmine
    host: localhost
    username: redmine
    password: %s
    encoding: utf8
    reconnect: true

test:
    adapter: sqlite3
    database: db/redmine.db
""" % env.db['pass'])


@task
def setup_http_server():
    setup_ssl_cert()
    if env.site['ssl']:
        if env.http_server == 'nginx':
            setup_nginx_https_server()
        else:
            setup_apache_https_server()

    else:
        if env.http_server == 'nginx':
            setup_nginx_server()
        else:
            setup_apache_server()


def setup_nginx_server():
    fabtools.require.nginx.server()
    nginx_conf = Path('/', 'etc', 'nginx', 'sites-available', 'redmine.conf')
    alias_conf = Path('/', 'etc', 'nginx', 'sites-enabled', 'redmine.conf')
    source = Path(env.local_root, 'etc', 'nginx', 'redmine.conf')
    sudo("rm -f %s" % nginx_conf)

    upload_template(
        filename=source,
        destination=Path('/', 'etc', 'nginx', 'sites-available', 'redmine.conf'),
        context={
            'project': env.project,
            'public': env.redmine['public'],
            'domain': env.site['domain'],
            'port': env.site['port'],
            'ip': env.site['ip']
        },
        use_sudo=True
    )
    sudo("chown root:root %s" % nginx_conf)
    sudo("rm -f %s" % alias_conf)
    sudo("ln -s %s %s" % (nginx_conf, alias_conf))
    setup_redmine_proxy()


def setup_redmine_proxy():
    source = Path(env.local_root, 'etc', 'nginx', 'redmine.proxy')
    target = Path('/', 'etc', 'nginx', 'redmine.proxy')
    put(source, target, use_sudo=True)


def setup_nginx_https_server():
    fabtools.require.nginx.server()
    nginx_conf = Path('/', 'etc', 'nginx', 'sites-available', 'redmine-ssl.conf')
    alias_conf = Path('/', 'etc', 'nginx', 'sites-enabled', 'redmine-ssl.conf')
    source = Path(env.local_root, 'etc', 'nginx', 'redmine-ssl.conf')
    sudo("rm -f %s" % nginx_conf)

    upload_template(
        filename=source,
        destination=Path('/', 'etc', 'nginx', 'sites-available', 'redmine-ssl.conf'),
        context={
            'project': env.project,
            'public': env.redmine['public'],
            'domain': env.site['domain'],
            'port': env.site['port'],
            'ip': env.site['ip']
        },
        use_sudo=True
    )
    sudo("chown root:root %s" % nginx_conf)
    sudo("rm -f %s" % alias_conf)
    sudo("ln -s %s %s" % (nginx_conf, alias_conf))
    setup_redmine_proxy()


def setup_apache_server():
    fabtools.require.file('/etc/apache2/sites-available/redmine.conf', """\
<VirtualHost *:80>
    ServerName {domain}
    DocumentRoot /home/redmine/redmine/public/

    <Proxy *>
        Order allow,deny
        Allow from all
    </Proxy>

    ProxyPreserveHost On
    ProxyTimeout 30

    <Proxy balancer://redmine_app>
        BalancerMember http://localhost:3000 max=1
        BalancerMember http://localhost:3001 max=1
        ProxySet maxattempts=3
        Allow from all
    </Proxy>

    RewriteEngine On
    RewriteCond {rewrite_cond}
    RewriteRule ^(.*) balancer://redmine_app/$1 [P,L]
</VirtualHost>
""".format(domain=env.site['domain'], rewrite_cond='%{LA-U:REQUEST_FILENAME} !-f'), use_sudo=True)

    sudo('a2ensite redmine.conf')
    sudo('a2enmod proxy')
    sudo('a2enmod proxy_http')
    sudo('a2enmod rewrite')
    sudo('a2enmod headers')
    sudo('a2enmod ssl')
    sudo('a2enmod proxy_balancer')
    sudo('a2enmod lbmethod_byrequests')


@task
def setup_apache_https_server():
    fabtools.require.file('/etc/apache2/sites-available/redmine.conf', """\
<VirtualHost *:80>
    ServerName {domain}

    Redirect / https://{domain}/
</VirtualHost>
<VirtualHost *:443>
    ServerName {domain}

    DocumentRoot /home/redmine/redmine/public/

    SSLEngine On
    SSLCertificateFile /etc/ssl/localcerts/redmine.pem
    SSLCertificateKeyFile /etc/ssl/localcerts/redmine.key

    <Proxy *>
        Order allow,deny
        Allow from all
    </Proxy>

    ProxyPreserveHost On
    ProxyTimeout 30

    <Proxy balancer://redmine_app>
        BalancerMember http://localhost:3000 max=1
        BalancerMember http://localhost:3001 max=1
        ProxySet maxattempts=3
        Allow from all
    </Proxy>

    RewriteEngine On
    RewriteCond {rewrite_cond}
    RewriteRule ^(.*) balancer://redmine_app/$1 [P,L]

    RequestHeader set X_FORWARDED_PROTO 'https'
</VirtualHost>
""".format(domain=env.site['domain'], rewrite_cond='%{LA-U:REQUEST_FILENAME} !-f'), use_sudo=True)

    sudo('a2ensite redmine.conf')
    sudo('a2enmod proxy')
    sudo('a2enmod proxy_http')
    sudo('a2enmod rewrite')
    sudo('a2enmod headers')
    sudo('a2enmod ssl')
    sudo('a2enmod proxy_balancer')
    sudo('a2enmod lbmethod_byrequests')


def setup_ssl_cert():
    if not fabtools.files.is_file('/etc/ssl/localcerts/redmine.key'):
        fabtools.require.file('/tmp/openssl.cnf', """\
[ req ]
prompt = no
distinguished_name = req_distinguished_name

[ req_distinguished_name ]
C = FR
ST = French
L = Pars
O = Example
OU = Org Unit Name
CN = Common Name
emailAddress = contact@example.com
""", use_sudo=True)
        sudo('mkdir -p /etc/ssl/localcerts')
        sudo('openssl req -config /tmp/openssl.cnf -new -x509 -days 365 -nodes -out /etc/ssl/localcerts/redmine.pem -keyout /etc/ssl/localcerts/redmine.key')
        sudo('rm /tmp/openssl.cnf')
        sudo('pip install mercurial')
        with settings(abort_exception=FabricException):
            try:
                restart_services()
            except FabricException:
                pass


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

    print("\n".join(report))


@task
def restart_services():
    if env.http_server == 'apache2':
        sudo('service nginx stop')
        fabtools.require.service.restarted('apache2')
    else:
        with settings(abort_exception=FabricException):
            try:
                sudo('killall uwsgi')
            except FabricException:
                pass
        fabtools.require.service.restarted('nginx')
        fabtools.require.service.restarted('supervisor')

    if 'cache_server' in env:
        if env.cache_server == 'redis':
            fabtools.require.service.restarted('redis-server')

        if env.cache_server == 'memcache':
            fabtools.require.service.restarted('memcached')

    if env.db['driver'] == 'mysql':
        fabtools.require.service.restarted('mysql-server')

    if env.db['driver'] == 'pgsql':
        fabtools.require.service.restarted('postgresql')

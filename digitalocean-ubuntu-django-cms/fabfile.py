import os
from fabric.api import *
from unipath import Path
from contextlib import contextmanager
from fabric.contrib.files import upload_template
from fabric.api import settings
from fabric.colors import green
import fabtools


def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))


class FabricException(Exception):
    pass


# the servers where the commands are executed
env.hosts = ['demo.loc']
env.project = 'mycms'

# the user to use for the remote commands
env.user = 'vagrant'
env.password = 'vagrant'
env.user_pwd = 'vagrant'

env.http_server = 'nginx'  # apache2|nginx
env.wsgi = 'uwsgi'  # gunicorn | uwsgi

# PostgreSQL	django.db.backends.postgresql_psycopg2	postgres://USER:PASSWORD@HOST:PORT/NAME
# PostGIS	    django.contrib.gis.db.backends.postgis	postgis://USER:PASSWORD@HOST:PORT/NAME
# MySQL	        django.db.backends.mysql	            mysql://USER:PASSWORD@HOST:PORT/NAME
# MySQL  (GIS)	django.contrib.gis.db.backends.mysql	mysqlgis://USER:PASSWORD@HOST:PORT/NAME
# SQLite	    django.db.backends.sqlite3	            sqlite:///PATH
# Oracle	    django.db.backends.oracle	            oracle://USER:PASSWORD@HOST:PORT/NAME
# Oracle (GIS)	django.contrib.gis.db.backends.oracle	oraclegis://USER:PASSWORD@HOST:PORT/NAME

env.services = [
    'nginx',
    'apache2',
    'supervisor',
    'mysql',
    'postgres'
]

env.db = {
    'root': genpass(),
    'name': env.project,
    'user': env.project,
    'pass': genpass(),
    'host': 'localhost',
}

#  PostgreSQL
env.db_server = 'pgsql'  # you can choose from mysql|postgresql|sqlite
env.db['port'] = 5432
env.db['url'] = 'postgres://%(user)s:%(pass)s@%(host)s:%(port)d/%(name)s' % env.db

#  MySQL
# env.db_server = 'mysql'  # you can choose from mysql|pgsql|sqlite
# env.db['port'] = 3306
# env.db['url'] = 'mysql://%(user)s:%(pass)s@%(host)s:%(port)d/%(name)s' % env.db

env.db_str = ''  # db setting string for django settings.py file
env.cache_server = 'memcache'  # memcache redis django
env.cache_str = None

env.home = Path('/', 'home', env.user)
env.ssh = '/home/%s/.ssh' % env.user

env.local_root = Path(__file__).ancestor(1)
env.local_proj = Path(env.local_root, 'project')

env.projects_dir = Path('/', 'home', env.user, 'projects')
env.project_dir = Path(env.projects_dir, env.project)
env.docroot = Path(env.project_dir)
env.downloads = Path('/', 'home', env.user, 'downloaded')

env.site = {
    'domain': 'example.com',  # without www.
    'docroot': env.docroot,
    'ssl': False,
    'port': 80,
    'login': 'admin',
    'admin': 'vasili.pascal@gmail.com',
    'admin_pwd': genpass()
}

env.redis = {
    'port': 6379,
    'pass': 'test',
    'clients': [
        '127.0.0.1',
        'localhost',
        env.site['domain']
    ]
}

env.memcache = {
    'port': 11211,
    'pass': 'test',
    'clients': [
        '127.0.0.1',
        'localhost',
        env.site['domain']
    ]
}

env.venv = Path(env.home, 'env')
env.packages = Path(env.venv, 'lib', 'python2.7', 'site-packages')
env.activate = 'source ' + env.venv + '/bin/activate'
env.pip = os.path.join(env.venv, 'bin/pip')
env.python = os.path.join(env.venv, Path('bin', 'python'))
env.gunicorn = os.path.join(env.venv, Path('bin', 'gunicorn'))
env.uwsgi = os.path.join(env.venv, Path('bin', 'uwsgi'))


@contextmanager
def source_virtualenv():
    with prefix(env.activate):
        yield


@task
def setup():
    sudo('apt-get update && apt-get -y dist-upgrade')

    fabtools.require.deb.packages([
        'imagemagick', 'libxml2-dev', 'libxml2',
        'libxslt1.1', 'libevent-2.0-5', 'libsasl2-2',
        'libldap-2.4-2', 'python-dev', 'libjpeg-dev', 'libpcre3',
        'libpcre3-dev', 'nginx', 'supervisor', 'python-pip',
        'python-virtualenv', 'gunicorn', 'fabric',
        'python-unipath', 'git', 'ufw',
        'libxml2-dev', 'libxslt1-dev', 'zlib1g-dev',
        'libsasl2-dev', 'libldap2-dev', 'libssl-dev',
        'python-pil', 'python-nose'
    ])

    fabtools.require.user(env.user, password=env.user_pwd)

    run("rm -rf %s" % env.venv)
    sudo("rm -rf %s" % env.projects_dir)
    sudo("mkdir -p %s" % env.projects_dir, user=env.user)
    run("rm -rf %s/manage.py" % env.projects_dir)

    with cd(env.home):
        run('virtualenv env')

    if env.db_server == 'pgsql':
        setup_pgsql()
    if env.db_server == 'mysql':
        setup_mysql()

    with cd(env.projects_dir):
        with source_virtualenv():
            # run(env.pip + " install djangocms-installer")
            run(env.pip + " install https://github.com/nephila/djangocms-installer/archive/master.zip")
            with settings(abort_exception=FabricException):
                try:
                    run("djangocms --no-input --verbose --db=%(url)s --filer -s -p . %(project)s"
                        % {'url': env.db['url'], 'project': env.project}
                    )
                except FabricException:
                    pass

    setup_project_group()

    if env.http_server == 'apache2':
        setup_django_apache()

    if env.http_server == 'nginx':
        if env.wsgi == 'gunicorn':
            setup_nginx_gunicorn()
        else:
            setup_nginx_uwsgi()

    create_admin()
    setup_static()
    report()
    restart_services()


@task
def setup_static():
    sudo('rm -rf %s/static' % env.project_dir)
    sudo('rm -rf %s/static' % env.projects_dir)
    run('mkdir %s/static' % env.projects_dir)
    run('mkdir %s/static' % env.project_dir)

    with cd(env.projects_dir):
        run(env.python + ' manage.py collectstatic -l --noinput')

    run('ln -s %(projects_dir)s/static %(project_dir)s/static' %
        {'projects_dir': env.projects_dir, 'project_dir': env.project_dir })



@task
def create_admin():
    with cd(env.projects_dir):
        with source_virtualenv():
            # run('python manage.py createsuperuser --username=admin --email=%s --noinput' % env.site['admin'])
            run(""" echo "from django.contrib.auth.models import User;
User.objects.create_superuser('%(login)s', '%(admin)s', '%(admin_pwd)s')" | """ % env.site + env.python + """ %s/manage.py shell
""" % env.projects_dir)


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

        # if env.cache_server == 'redis':
        #     fabtools.require.service.restarted('redis-server')
        #
        # if env.cache_server == 'memcache':
        #     fabtools.require.service.restarted('memcached')


def setup_project_group():
    sudo('addgroup --quiet --system %(project)s' % {'project': env.project})
    sudo('adduser --quiet --system --ingroup %(project)s --no-create-home --no-create-home %(project)s'
         % {'project': env.project})

    print(green('System user %s created.' % env.project))


def setup_pgsql():
    fabtools.require.postgres.server()
    fabtools.require.deb.packages(['postgresql-server-dev-9.3', 'postgresql-client', 'python-psycopg2'])
    fabtools.require.postgres.user(env.db['user'], env.db['pass'])
    fabtools.require.postgres.database(env.db['name'], owner=env.db['user'])
    fabtools.require.service.started('postgresql')
    print(green('PostgreSQL installed and running.'))


def setup_mysql():
    fabtools.require.deb.packages(['python-mysqldb', 'libmysqlclient-dev'])

    with source_virtualenv():
        run(env.pip + ' install mysql-python')

    fabtools.require.mysql.server(password=env.db['root'])

    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.user(env.db['user'], env.db['pass'])
    with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.database(env.db['name'], owner=env.db['user'])

    fabtools.require.service.started('mysql')
    print(green('MySQL installed and running.'))


def setup_nginx_gunicorn():
    fabtools.require.nginx.server()
    tpl = 'site-gunicorn.conf'
    nginx_conf = Path('/', 'etc', 'nginx', 'sites-available', tpl)
    alias_conf = Path('/', 'etc', 'nginx', 'sites-enabled', tpl)
    source = Path(env.local_root, 'etc', 'nginx', tpl)
    sudo("rm -f %s" % nginx_conf)

    upload_template(
        filename=source,
        destination=Path('/', 'etc', 'nginx', 'sites-available'),
        context={
            'docroot': env.docroot,
            'domain': env.site['domain'],
            'port': env.site['port'],
            'ip': '127.0.0.1'
        },
        use_sudo=True
    )
    sudo("chown root:root %s" % nginx_conf)
    sudo("rm -f %s" % alias_conf)
    sudo("ln -s %s %s" % (nginx_conf, alias_conf))
    setup_supervisor_gunicorn()
    print(green('Nginx configured with gunicorn.'))


def setup_nginx_uwsgi():
    fabtools.require.nginx.server()
    tpl = 'site-uwsgi.conf'

    nginx_conf = Path('/', 'etc', 'nginx', 'sites-available', tpl)
    alias_conf = Path('/', 'etc', 'nginx', 'sites-enabled', tpl)

    source = Path(env.local_root, 'etc', 'nginx', tpl)

    sudo("rm -f %s" % nginx_conf)

    upload_template(
        filename=source,
        destination=Path('/', 'etc', 'nginx', 'sites-available'),
        context={
            'docroot': env.docroot,
            'project': env.project,
            'domain': env.site['domain'],
            'port': env.site['port'],
            'ip': '127.0.0.1'
        },
        use_sudo=True
    )
    sudo("chown root:root %s" % nginx_conf)
    sudo("rm -f %s" % alias_conf)
    sudo("ln -s %s %s" % (nginx_conf, alias_conf))
    setup_supervisor_uwsgi()
    print(green('Nginx configured with uwsgi.'))


def setup_supervisor_gunicorn():
    with source_virtualenv():
        run(env.pip + ' install gunicorn')
    super_conf = Path('/', 'etc', 'supervisor', 'conf.d', '%s.conf' % env.project)
    with settings(abort_exception=FabricException):
        try:
            sudo("rm -f %s" % super_conf)
        except FabricException:
            pass

    source = Path(env.local_root, 'etc', 'supervisor', 'gunicorn.conf')
    upload_template(
        filename=source,
        destination=super_conf,
        context={
            'gunicorn_path': env.gunicorn,
            'project': env.project,
            'project_dir': env.project_dir,
            'projects_dir': env.projects_dir,
        },
        use_sudo=True
    )
    sudo("chown root:root %s" % super_conf)

    tpl = 'gunicorn.conf.py'
    upload_template(
        filename=Path(env.local_root, 'etc', 'gunicorn', tpl),
        destination=env.project_dir,
    )
    print(green('Supervisor installed.'))


def setup_supervisor_uwsgi():
    with source_virtualenv():
        run(env.pip + ' install uwsgi')

    tpl = 'uwsgi.conf'
    super_conf = Path("/", 'etc', 'supervisor', 'conf.d', tpl)

    with settings(abort_exception=FabricException):
        try:
            sudo("rm -f %s" % super_conf)
        except FabricException:
            pass
    source = Path(env.local_root, 'etc', 'supervisor', tpl)

    upload_template(
        filename=source,
        destination=super_conf,
        context={
            'project_dir': env.project_dir,
            'project': env.project,
            'procname': '%(program_name)s_%(process_num)02d',
            'uwsgi_path': env.uwsgi,
            'user': env.user
        },

        use_sudo=True
    )
    tpl = 'gs.xml'
    upload_template(
        filename=Path(env.local_root, 'etc', 'uwsgi', tpl),
        destination=env.project_dir,
        context={
            'project_dir': env.project_dir,
            'projects_dir': env.projects_dir,
            'project': env.project,
            'procname': '%(program_name)s_%(process_num)02d',
            'uwsgi_path': env.uwsgi,
            'venv': env.venv,
        }
    )
    sudo("chown root:root %s" % super_conf)
    print(green('Supervisor installed.'))


def setup_django_apache():
    green('Setup apache mode')

    with settings(abort_exception=FabricException):
        try:
            sudo('service nginx stop')
        except FabricException:
            pass
    apache_dir = Path(env.project_dir, 'apache')
    with settings(abort_exception=FabricException):
        try:
            run('mkdir ' + apache_dir)
        except FabricException:
            pass

    # next block can be commented because djangocms creates wsgi.py
    # wsgi_script = 'django.wsgi'
    # wsgi_remote_path = Path(apache_dir, wsgi_script)
    # wsgi_local_path = Path(env.local_root, 'etc', 'apache', wsgi_script)
    #
    # upload_template(
    #     filename=wsgi_local_path,
    #     destination=wsgi_remote_path,
    #     context={
    #         'path_to_django': env.packages,
    #         'path_to_project': env.project_dir,
    #         'project': env.project
    #     }
    # )
    setup_apache_mod_wsgi()


def setup_apache_mod_wsgi():
    fabtools.require.apache.server()
    sudo('apt-get -y install libapache2-mod-wsgi')
    fabtools.require.apache.enable_module('wsgi')
    fabtools.require.apache.enable_module('rewrite')

    with open('./etc/apache/site.conf') as fn:
        config = fn.read()

    # wsgi = Path(env.project_dir, 'apache', 'django.wsgi')
    wsgi = Path(env.docroot, 'wsgi.py')

    fabtools.require.apache.site(
        env.site['domain'],
        template_contents=config,
        check_config=False,
        port=env.site['port'],
        hostname=env.site['domain'],
        document_root=env.site['docroot'],
        user=env.user,
        project=env.project,
        admin=env.site['admin'],
        envpackages=env.packages,
        wsgi=wsgi,
        project_dir=env.project_dir,
        projects_dir=env.projects_dir,
        appgroup='%{GLOBAL}'
    )
    sudo('mv /etc/apache2/envvars /tmp/envvars')
    put('./etc/apache/envvars', '/etc/apache2/envvars', use_sudo=True)
    print(green('Apache mod_wsgi installed.'))


@task
def destroy_mysql():
    with settings(abort_exception=FabricException):
        try:
            sudo('service mysql stop')  # or mysqld
            sudo('killall -9 mysql')
            sudo('killall -9 mysqld')
        except FabricException:
            pass
    sudo('apt-get -y remove --purge mysql-server mysql-client mysql-common')
    sudo('apt-get -y autoremove')
    sudo('apt-get -y autoclean')
    sudo('deluser mysql')
    sudo('rm -rf /var/lib/mysql')
    sudo('apt-get -y purge mysql-server-core-5.5')
    sudo('apt-get -y purge mysql-client-core-5.5')
    sudo('rm -rf /var/log/mysql')
    sudo('rm -rf /etc/mysql')


@task
def destroy_postgresql():
    with settings(abort_exception=FabricException):
        try:
            sudo('service postgresql stop')
            sudo('killall psql')
        except FabricException:
            pass
    sudo('apt-get -y  --purge remove postgresql\*')
    with settings(abort_exception=FabricException):
        try:
            sudo('rm -r /etc/postgresql/')
        except FabricException:
            pass
    with settings(abort_exception=FabricException):
        try:
            sudo('rm -r /etc/postgresql-common/')
            sudo('rm -r /var/lib/postgresql/')
        except FabricException:
            pass

    sudo('userdel -r postgres')
    sudo('groupdel postgres')


@task
def destroy_apache():
    fabtools.service.stop('apache2')
    fabtools.deb.uninstall(['apache2'], purge=True, options=None)
    sudo('rm -f /etc/apache2/sites-available/*')
    sudo('rm -f /etc/apache2/sites-enabled/*')
    # sudo('apt-get purge apache2*')


@task
def destroy_nginx():
    fabtools.service.stop('nginx')
    fabtools.deb.uninstall(['nginx'], purge=True, options=None)
    sudo('rm -f /etc/nginx/sites-available/*')
    sudo('rm -f /etc/nginx/sites-enabled/*')


@task
def destroy_supervisor():
    fabtools.service.stop('supervisor')
    fabtools.deb.uninstall(['supervisor'], purge=True, options=None)
    sudo('apt-get purge supervisor*')


@task
def install_sphix():
    sudo('add-apt-repository ppa:builds/sphinxsearch-rel22')
    sudo('apt-get update')
    sudo('apt-get install sphinxsearch')


def setup_solr():
    with source_virtualenv():
        run(env.pip + " install pysolr")

    with settings(abort_exception=FabricException):
        try:
            sudo('mkdir %s' % env.downloads, user=env.user)
        except FabricException:
            pass

    with cd(env.projects_dir):
        run('wget http://archive.apache.org/dist/lucene/solr/4.7.2/solr-4.7.2.tgz')
        run('tar xzf solr-4.7.2.tgz')
        with cd('solr-4.7.2/example/solr/collection1'):
            with settings(abort_exception=FabricException):
                try:
                    run('mv conf conf.original')
                    run('ln -s %s/sites/sandbox/deploy/solr conf' % env.oscar_dir)
                except FabricException:
                    pass

        # start solr
        with cd('solr-4.7.2/example'):
            setup_java()

    setup_solr_supervisor()
    print(green('Solr installed.'))


def setup_java():
    sudo('add-apt-repository -y ppa:webupd8team/java')
    sudo('apt-get update')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 select true | debconf-set-selections')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 seen true | debconf-set-selections')
    sudo('apt-get -q -y install oracle-java8-installer')
    print(green('Java installed.'))


def setup_solr_supervisor():
    tpl = 'solr.conf'
    super_conf = Path("/", 'etc', 'supervisor', 'conf.d', tpl)

    with settings(abort_exception=FabricException):
        try:
            sudo("rm -f %s" % super_conf)
        except FabricException:
            pass

    source = Path(env.local_root, 'etc', 'supervisor', tpl)
    solr_path = Path(env.downloads, 'solr-4.7.2','example')  # path to start.jar

    upload_template(
        filename=source,
        destination=super_conf,
        context={
            'solr_path': solr_path,
        },
        use_sudo=True
    )
    sudo("chown root:root %s" % super_conf)
    print(green('Solr added to supervisor.'))

def sphinx_start():
    sudo('service sphinxsearch start')

def secure_solr():
    pass


@task
def destroy_all():
    with settings(abort_exception=FabricException):
        try:
            destroy_mysql()
        except FabricException:
            pass
    with settings(abort_exception=FabricException):
        try:
            destroy_postgresql()
        except FabricException:
            pass
    destroy_nginx()
    destroy_apache()


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
    report.append(env.db_server)
    dbs = []
    for k, v in env.db.items():
        dbs.append(str(k) + ': ' + str(v))
    report.append("\n".join(dbs))

    report.append("\n" + 20 * '=' + ' Cache server ' + 20 * '=')
    report.append(env.cache_server)
    dbs = []
    for k, v in env.redis.items():
        dbs.append(str(k) + ': ' + str(v))
    report.append("\n".join(dbs))
    print("\n".join(report))

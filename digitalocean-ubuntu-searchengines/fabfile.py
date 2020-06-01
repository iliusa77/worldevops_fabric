"""

how to run:  fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10,engine={sphinx,solr,elastic} setup

"""
from fabric.api import *
from fabtools import require
import fabtools
import requests
from unipath import Path
from fabric.contrib.files import upload_template
from fabric.colors import green
import sys
root = Path(__file__).ancestor(2)
sys.path.append(root)
from worldevops import *


env.db = {
    'driver': 'mysql',
    'host': 'localhost',
    'name': 'test',
    'user': 'root',
    'port': 3306,
    'root': genpass(),
    'pass': genpass(),
    'query': 'SELECT id, group_id, UNIX_TIMESTAMP(date_added) AS date_added, title, content FROM documents',
    'uint': 'group_id',
    'timestamp': 'date_added',
    'query_info': 'SELECT * FROM documents WHERE id=$id'
}

env.elastic = {
    'cluster_name': 'My node',
    'node_name': 'mycluster1',
    'path_data': '/var/lib/elasticsearch',
    'host': 'localhost',
    'port': 9200,
}

env.solr = {
    'path': '/opt'
}

def setup_java():
    sudo('add-apt-repository -y ppa:webupd8team/java')
    sudo('apt-get update')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 select true | sudo debconf-set-selections')
    sudo('echo debconf shared/accepted-oracle-license-v1-1 seen true | sudo debconf-set-selections')
    sudo('apt-get install -y oracle-java8-installer')


def setup_sphinx():
    sudo('add-apt-repository -y ppa:builds/sphinxsearch-rel22')
    sudo('apt-get update && apt-get -y dist-upgrade')
    install_mysql()
    fabtools.require.deb.packages([
                'mysql-client',
                'unixodbc',
                'libpq5'
            ])
    sudo('apt-get -y install sphinxsearch')
    sudo('chmod 777 /var/log/sphinxsearch/searchd.log')
    sudo('chmod 777 /var/log/sphinxsearch/query.log')
    sudo('echo "%s" | mysql --user="%s" --password="%s"' % ('USE test', 'root', env.db['root']))
    sudo('echo "%s" | mysql --user="%s" --password="%s"' % ('SOURCE /usr/share/doc/sphinxsearch/example-conf/example.sql', 'root', env.db['root']))
    upload_template(
        './config/sphinx/sphinx.conf',
        '/etc/sphinxsearch/sphinx.conf',
        use_sudo=True,
        context={'db_driver': env.db['driver'], 'db_host': env.db['host'], 'db_name': env.db['name'],
                 'db_user': env.db['user'], 'db_password': env.db['root'], 'db_port': env.db['port'],
                 'db_query': env.db['query'], 'db_uint': env.db['uint'], 'db_timestamp': env.db['timestamp']}
    )
    sudo('indexer --all --rotate')
    put('./config/sphinx/sphinxsearch', '/etc/default/sphinxsearch', use_sudo=True)
    fabtools.service.restart('sphinxsearch')
    setup_supervisor()
    add_to_supervisor('sphinx')
    report('sphinx')


def setup_solr():
    setup_java()
    with cd(env.solr['path']):
        sudo('wget http://archive.apache.org/dist/lucene/solr/4.7.2/solr-4.7.2.tgz')
        sudo('tar -xvf solr-4.7.2.tgz')
        sudo('cp -R solr-4.7.2/example /opt/solr')
    sudo('useradd -d %s/solr -s /sbin/false solr' % env.solr['path'])
    sudo('chown solr:solr -R %s/solr' % env.solr['path'])
    setup_supervisor()
    add_to_supervisor('solr')
    report('solr')


def setup_elastic():
    sudo('apt-get update && apt-get -y dist-upgrade')
    setup_java()
    sudo('wget -qO - https://packages.elastic.co/GPG-KEY-elasticsearch | sudo apt-key add -')
    sudo('echo "deb https://packages.elastic.co/elasticsearch/2.x/debian stable main" | sudo tee -a /etc/apt/sources.list.d/elasticsearch-2.x.list')
    sudo('apt-get update')
    sudo('apt-get install -y elasticsearch')
    sudo('update-rc.d elasticsearch defaults 95 10')
    upload_template(
        './config/elastic/elasticsearch.yml',
        '/etc/elasticsearch/elasticsearch.yml',
        use_sudo=True,
        context={'cluster_name': env.elastic['cluster_name'], 'node_name': env.elastic['node_name'],
                 'path_data': env.elastic['path_data'], 'host': env.elastic['host'], 'port': env.elastic['port']}
    )
    fabtools.service.start('elasticsearch')
    setup_supervisor()
    add_to_supervisor('elastic')
    report('elastic')


def setup_supervisor():
    fabtools.require.deb.packages([
            'supervisor'
        ])
    fabtools.service.restart('supervisor')


def setup():
    if env.engine == 'sphinx':
        setup_sphinx()
    if env.engine == 'solr':
        setup_solr()
    if env.engine == 'elastic':
        setup_elastic()


def add_to_supervisor(what):
    if what == 'sphinx':
        put('./config/supervisor/sphinx.conf',Path("/", 'etc', 'supervisor', 'conf.d'), use_sudo = True)
        sudo("chown root:root %s" % Path("/", 'etc', 'supervisor', 'conf.d', 'sphinx.conf'))
    if what == 'elastic':
        put('./config/supervisor/elastic.conf',Path("/", 'etc', 'supervisor', 'conf.d'), use_sudo = True)
        sudo("chown root:root %s" % Path("/", 'etc', 'supervisor', 'conf.d', 'elastic.conf'))
    if what == 'solr':
        upload_template(
            './config/supervisor/solr.conf',
            Path("/", 'etc', 'supervisor', 'conf.d'),
            context={'solr_path': '%s/solr' % env.solr['path']},
            use_sudo=True
        )
    sudo('supervisorctl reread')
    sudo('supervisorctl update')


def destroy_sphinx():
    destroy_mysql()
    fabtools.deb.uninstall(['sphinxsearch'], purge=True, options=None)
    sudo('rm %s' % Path("/", 'etc', 'supervisor', 'conf.d', 'sphinx.conf'))
    sudo('supervisorctl reread')
    sudo('supervisorctl update')


def destroy_elastic():
    fabtools.deb.uninstall(['elasticsearch','oracle-java8-installer'], purge=True, options=None)
    sudo('rm %s' % Path("/", 'etc', 'supervisor', 'conf.d', 'elastic.conf'))
    sudo('supervisorctl reread')
    sudo('supervisorctl update')


def destroy_solr():
    fabtools.deb.uninstall(['oracle-java8-installer'], purge=True, options=None)
    sudo('rm -rf /var/solr')
    sudo('rm -rf /opt/solr-4.7.2')
    sudo('rm -rf /opt/solr')
    sudo('rm -f /etc/init.d/solr')
    sudo('deluser --remove-home solr')
    sudo('rm %s' % Path("/", 'etc', 'supervisor', 'conf.d', 'solr.conf'))
    sudo('supervisorctl reread')
    sudo('supervisorctl update')


def destroy_supervisor():
    fabtools.service.stop('supervisor')
    fabtools.deb.uninstall(['supervisor'], purge=True, options=None)
    sudo('apt-get purge supervisor*')


def report(type):
    run('clear')
    if type == 'sphinx':
        print('SphinxSearch is installed with sample data')
        print('SphinxSearch configuration is available in /etc/sphinxsearch/sphinx.conf file')
        print('Full configuration file with comments is available in /usr/share/doc/sphinxsearch/example-conf/ directory')
        print(green('------------------------------------'))
        print(green('MYSQL database'))
        print(green('------------------------------------'))
        print('Host: %s' % env.db['host'])
        print('Database name: %s' % env.db['name'])
        print('Database user: %s' % env.db['user'])
        print('Database root user password: %s' % env.db['root'])
    if type == 'elastic':
        print('ElasticSearch is installed with sample configuration')
        print('ElasticSearch configuration is available in /etc/elasticsearch/elasticsearch.yml file')
        print('Cluster name: %s' %env.elastic['cluster_name'])
        print('Node name: %s' %env.elastic['node_name'])
        print('Data path: %s' %env.elastic['path_data'])
        print('Host: %s' %env.elastic['host'])
        print('Port: %s' %env.elastic['port'])
    if type == 'solr':
        print('Solr is installed in %s/solr directory' % env.solr['path'])
        print('You can access it by http://%s:8983/solr' % env.host)
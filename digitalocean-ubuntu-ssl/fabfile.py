from fabtools import require
from unipath import Path
from fabric.colors import red
from fabric.contrib.files import upload_template
from fabric.api import run, env, sudo
import sys
from worldevops import *

sitename = 'site'
commonname = '%s.com' % sitename

#Change to client company details
env.reqdata = {
    'country': 'GB',
    'state': 'Nottingham',
    'locality': 'Nottinghamshire',
    'organization': '{}'.format(commonname),
    'organizationalunit': 'IT',
    'email': 'administrator@{}'.format(commonname),
    'commonname': commonname
}

env.site = {
    'domain': commonname,  # without www.
    'docroot': Path('/', 'home', 'vagrant/{}').format(commonname),
    'ssl': True,
    'certfile': '/home/vagrant/{0}/ssl/{0}'.format(commonname),
    'keyfile': '/home/vagrant/{0}/ssl/{0}'.format(commonname)
}

#Generation of certificates
def gen_openssl():
    sudo('mkdir /open-ssl-keys')
    with cd('/open-ssl-keys'):
        sudo('openssl genrsa -out rootCA.key 2048')
        sudo('openssl req -x509 -new -key rootCA.key -days 10000 -out rootCA.crt \
        -subj "/C=%(country)s/ST=%(state)s/L=%(locality)s/O=%(organization)s/OU=%(organizationalunit)s/CN=%(commonname)s/emailAddress=%(email)s"' % env.reqdata)

        sudo('openssl genrsa -out {}.key 2048'.format(commonname))
        sudo('openssl req -new -key %(commonname)s.key -out %(commonname)s.csr \
        -subj "/C=%(country)s/ST=%(state)s/L=%(locality)s/O=%(organization)s/OU=%(organizationalunit)s/CN=%(commonname)s/emailAddress=%(email)s"' % env.reqdata)

        sudo('openssl x509 -req -in {0}.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out {0}.crt -days 5000'.format(commonname))


def config_apache():
    with open('./apache/site.conf') as fn:
        config_tpl = fn.read()

    fabtools.require.apache.site(
        commonname,
        template_contents=config_tpl,
        port=80,
        domain=sitename,
        docroot='/home/vagrant/{}'.format(commonname)
    )

def config_apache_https():
    with open('./apache/site-ssl.conf') as fn:
        config_tpl = fn.read()

    fabtools.require.apache.site(
        commonname,
        template_contents=config_tpl,
        port=443,
        domain=sitename,
        docroot='/home/vagrant/{}'.format(commonname),
        certfile='/home/vagrant/{0}/ssl/{0}'.format(commonname),
        keyfile='/home/vagrant/{0}/ssl/{0}'.format(commonname),
        sslpath='/home/vagrant/{}/ssl/'.format(commonname),
        cacertfile='/home/vagrant/{}/ssl/rootCA'.format(commonname)
    )


def setup_apache():
    sudo("apt-get update")
    sudo('mkdir -p /home/vagrant/{0}/ssl && cp -rp /open-ssl-keys/* /home/vagrant/{0}/ssl/'.format(commonname))
    fabtools.require.apache.server()
    sudo('echo "ServerName {}" > /etc/apache2/conf-available/fqdn.conf'.format(commonname))
    config_apache()
    config_apache_https()
    sudo('a2enconf fqdn')
    fabtools.require.apache.enable_module('rewrite')
    fabtools.require.apache.enable_module('ssl')
    fabtools.service.reload('apache2')
    sudo('cp -rp /var/www/html/* /home/vagrant/{}/'.format(commonname))
    sudo('rm -rf /open-ssl-keys/')


def setup_nginx():
    sudo("apt-get update")
    fabtools.require.nginx.server()
    sudo('mkdir -p /home/vagrant/{0}/ssl && cp -rp /open-ssl-keys/* /home/vagrant/{0}/ssl/'.format(commonname))

    if env.site['ssl'] == True:
        upload_template(
            filename=Path('./', 'nginx', 'ssl-site.conf'),
            destination='/etc/nginx/sites-available/ssl-site.conf',
            context=env.site, use_sudo=True
        )
    else:
        upload_template(
            filename=Path('./', 'nginx', 'site.conf'),
            destination='/etc/nginx/sites-available/site.conf',
            context=env.site, use_sudo=True
        )

    sudo("ln -s /etc/nginx/sites-available/ssl-site.conf /etc/nginx/sites-enabled/ssl-site.conf")
    fabtools.service.reload('nginx')
    sudo('cp -rp /usr/share/nginx/html/* /home/vagrant/{}/'.format(commonname))
    sudo('rm -rf /open-ssl-keys/')


def setup():
    gen_openssl()
    setup_apache()
    #setup_nginx()


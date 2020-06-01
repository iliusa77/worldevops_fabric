# -*- coding: utf-8 -*-
# for Ubuntu 14.04
# installation postfix + postfixadmin + dovecot

'''
how to run: fab -H demo.loc --user vagrant --password vagrant <command>

'''
import sys
import os
import time
from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path
from fabric.contrib.files import upload_template
from jinja2 import *
from fabric.colors import blue, green, red
root = Path(__file__).ancestor(3)
sys.path.append(root)

user = 'vagrant'
password = 'vagrant'
project = 'postfix'
hostname = 'mail'
ip = '192.168.33.10'
domain = 'demo.loc'
commonname = 'mail.demo.loc'
postfixadmin_user = 'postfixadmin'
postfixadminpassword = 'Quai5oga'
postfixadmin_hosts = '127.0.0.1'
postfixadmin_dbname = 'postfixadmin'
env.local_root = Path(__file__).ancestor(2)

env.db = {
  'root': '',
  'user': postfixadmin_user,
  'pass': postfixadminpassword,
  'name': postfixadmin_dbname,
  'host': 'localhost'
}


def common_setup():
  sudo('apt-get update')
  fabtools.require.deb.packages([
    'postfix', 'postfix-mysql', 'libsasl2-modules', 'libsasl2-modules-sql',
    'postfixadmin', 'php5-fpm', 'php5-imap', 'php5-mysql', 'php5-mcrypt', 'php5-intl',
    'ssl-cert', 'mysqmail-dovecot-logger', 'dovecot-sieve', 'dovecot-mysql', 'dovecot-managesieved',
    'dovecot-lmtpd', 'dovecot-imapd', 'dovecot-common', 'dovecot-antispam', 'opendkim', 'opendkim-tools'
  ])

def system_setup():
  sudo('echo "{0} {1} www.{1} mail.{1}" >> /etc/hosts'.format(ip, domain))
  sudo('sudo groupadd -g 5000 vmail')
  sudo('sudo useradd -g vmail -u 5000 vmail -d /dev/null -s /bin/false -M')
  sudo('adduser postfix sasl')
  sudo('mkdir /var/vmail')
  sudo('chown vmail:vmail /var/vmail')
  sudo('openssl req -new -x509 -days 3650 -nodes -out /etc/ssl/certs/dovecot.pem -keyout /etc/ssl/private/dovecot.pem')
  sudo('chmod o= /etc/ssl/private/dovecot.pem')
  sudo('openssl req -new -x509 -days 3650 -nodes -out /etc/ssl/certs/postfix.pem -keyout /etc/ssl/private/postfix.pem')
  sudo('chmod o= /etc/ssl/private/postfix.pem')


#Configuration Postfix

def configure_postfix_main():
  tpldir = str(Path('etc', 'postfix'))
  target = str(Path('/', 'etc', 'postfix', 'main.cf'))
  context = {
    'domain': domain,
    'commonname': commonname
  }
  upload_template(
    filename="main.cf",
    destination=target,
    context=context,
    use_jinja=True,
    template_dir=tpldir,
    use_sudo=True
  )

def configure_postfix_virtual_alias_maps():
  tpldir = str(Path('etc', 'postfix'))
  target = str(Path('/', 'etc', 'postfix', 'virtual-alias-maps.cf'))
  context = {
    'user': postfixadmin_user,
    'password': postfixadminpassword,
    'hosts': postfixadmin_hosts,
    'dbname':postfixadmin_dbname
  }
  upload_template(
    filename="virtual-alias-maps.cf",
    destination=target,
    context=context,
    use_jinja=True,
    template_dir=tpldir,
    use_sudo=True
  )

def configure_postfix_virtual_mailbox_domains():
  tpldir = str(Path('etc', 'postfix'))
  target = str(Path('/', 'etc', 'postfix', 'virtual-mailbox-domains.cf'))
  context = {
    'user': postfixadmin_user,
    'password': postfixadminpassword,
    'hosts': postfixadmin_hosts,
    'dbname': postfixadmin_dbname
  }
  upload_template(
    filename="virtual-mailbox-domains.cf",
    destination=target,
    context=context,
    use_jinja=True,
    template_dir=tpldir,
    use_sudo=True
  )

def configure_postfix_virtual_mailbox_maps():
  tpldir = str(Path('etc', 'postfix'))
  target = str(Path('/', 'etc', 'postfix', 'virtual-mailbox-maps.cf'))
  context = {
    'user': postfixadmin_user,
    'password': postfixadminpassword,
    'hosts': postfixadmin_hosts,
    'dbname':  postfixadmin_dbname
  }
  upload_template(
    filename="virtual-mailbox-maps.cf",
    destination=target,
    context=context,
    use_jinja=True,
    template_dir=tpldir,
    use_sudo=True
  )

def configure_postfix_master():
  source = Path('etc', 'postfix', 'master.cf')
  put(local_path=source, remote_path="/etc/postfix/", use_sudo=True)

def configure_postfix():
  configure_postfix_main()
  configure_postfix_virtual_alias_maps()
  configure_postfix_virtual_mailbox_domains()
  configure_postfix_virtual_mailbox_maps()
  configure_postfix_master()


#Configuration Dovecot

def configure_dovecot_sql_conf():
  tpldir = str(Path('etc', 'dovecot'))
  target = str(Path('/', 'etc', 'dovecot', 'dovecot-sql.conf'))
  context = {
    'user': postfixadmin_user,
    'password': postfixadminpassword,
    'hosts': postfixadmin_hosts,
    'dbname': postfixadmin_dbname
  }
  upload_template(
    filename="dovecot-sql.conf",
    destination=target,
    context=context,
    use_jinja=True,
    template_dir=tpldir,
    use_sudo=True
  )

def configure_dovecot_conf():
  source = Path('etc', 'dovecot', 'dovecot.conf')
  put(local_path=source, remote_path="/etc/dovecot/", use_sudo=True)

def configure_dovecot_10_auth_conf():
  source = Path('etc', 'dovecot', 'conf.d','10-auth.conf')
  put(local_path=source, remote_path="/etc/dovecot/conf.d/", use_sudo=True)

def configure_dovecot_auth_sql_conf_ext():
  source = Path('etc', 'dovecot', 'conf.d','auth-sql.conf.ext')
  put(local_path=source, remote_path="/etc/dovecot/conf.d/", use_sudo=True)

def configure_dovecot_10_logging_conf():
  source = Path('etc', 'dovecot', 'conf.d','10-logging.conf')
  put(local_path=source, remote_path="/etc/dovecot/conf.d/", use_sudo=True)

def configure_dovecot_10_ssl_conf():
  source = Path('etc', 'dovecot', 'conf.d','10-ssl.conf')
  put(local_path=source, remote_path="/etc/dovecot/conf.d/", use_sudo=True)

def configure_dovecot_10_mail_conf():
  source = Path('etc', 'dovecot', 'conf.d','10-mail.conf')
  put(local_path=source, remote_path="/etc/dovecot/conf.d/", use_sudo=True)

def configure_dovecot_15_lda_conf():
  tpldir = str(Path('etc', 'dovecot', 'conf.d'))
  target = str(Path('/', 'etc', 'dovecot', 'conf.d','15-lda.conf'))
  context = {
    'domain': domain,
    'commonname': commonname
  }
  upload_template(
    filename="15-lda.conf",
    destination=target,
    context=context,
    use_jinja=True,
    template_dir=tpldir,
    use_sudo=True
  )


def configure_dovecot_20_imap_conf():
  source = Path('etc', 'dovecot', 'conf.d','20-imap.conf')
  put(local_path=source, remote_path="/etc/dovecot/conf.d/", use_sudo=True)

def configure_dovecot_20_lmtp_conf():
  source = Path('etc', 'dovecot', 'conf.d','20-lmtp.conf')
  put(local_path=source, remote_path="/etc/dovecot/conf.d/", use_sudo=True)

def configure_dovecot_20_managesieve_conf():
  source = Path('etc', 'dovecot', 'conf.d','20-managesieve.conf')
  put(local_path=source, remote_path="/etc/dovecot/conf.d/", use_sudo=True)

def create_dovecot_init():
  source = Path('etc', 'init.d','dovecot')
  put(local_path=source, remote_path="/etc/init.d/", use_sudo=True)
  sudo('chmod a+x /etc/init.d/dovecot')

def configure_dovecot():
  configure_dovecot_sql_conf()
  configure_dovecot_conf()
  configure_dovecot_10_auth_conf()
  configure_dovecot_auth_sql_conf_ext()
  configure_dovecot_10_logging_conf()
  configure_dovecot_10_ssl_conf()
  configure_dovecot_10_mail_conf()
  configure_dovecot_15_lda_conf()
  configure_dovecot_20_imap_conf()
  configure_dovecot_20_lmtp_conf()
  configure_dovecot_20_managesieve_conf()
  create_dovecot_init()


def configure_apache():
  fabtools.require.apache.server()
  source = Path('etc', 'apache2','ports.conf')
  put(local_path=source, remote_path="/etc/apache2/", use_sudo=True)
  tpldir = str(Path('etc', 'apache2', 'sites-available'))
  target = str(Path('/', 'etc', 'apache2', 'sites-available','000-default.conf'))
  context = {
    'domain': domain
  }
  upload_template(
    filename="000-default.conf",
    destination=target,
    context=context,
    use_jinja=True,
    template_dir=tpldir,
    use_sudo=True
  )
  sudo('service apache2 restart')

def configure_mysql():
  with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.mysql.query('DROP USER `%s`@`localhost`' % env.db['user'],
            mysql_user='root',
            mysql_password=env.db['root']
          )
        fabtools.require.mysql.user(env.db['user'], env.db['pass'])
  with settings(mysql_user='root', mysql_password=env.db['root']):
        fabtools.require.mysql.database(env.db['name'], owner=env.db['user'])
        fabtools.mysql.query('GRANT ALL ON `{0}`.* TO `{1}`@`{2}`;'.format(
            env.db['name'], 
            env.db['user'], 
            env.db['host']
          ), 
            mysql_user='root',
            mysql_password=env.db['root']
        )
   
def configure_postfixadmin():
  source = Path('etc', 'postfixadmin', 'config.inc.php')
  put(local_path=source, remote_path="/etc/postfixadmin/", use_sudo=True)
  tpldir = str(Path('etc', 'postfixadmin'))
  target = str(Path('/', 'etc', 'postfixadmin', 'dbconfig.inc.php'))
  context = {
    'dbpass': postfixadminpassword,
  }
  upload_template(
    filename="dbconfig.inc.php",
    destination=target,
    context=context,
    use_jinja=True,
    template_dir=tpldir,
    use_sudo=True
  )

def configure_dkim():
  tpldir = str(Path('etc'))
  target = str(Path('/', 'etc', 'opendkim.conf'))
  context = {
    'domain': domain,
  }
  upload_template(
    filename="opendkim.conf",
    destination=target,
    context=context,
    use_jinja=True,
    template_dir=tpldir,
    use_sudo=True
  )
  sudo('echo "SOCKET="inet:8891@localhost"" >> /etc/default/opendkim')
  with cd('/etc/postfix'):
    sudo('opendkim-genkey -t -s dkim -d {}'.format(domain))
    sudo('mv dkim.private /etc/postfix/dkim.key')

def restart_services():
  sudo('service postfix restart')
  time.sleep(5)
  sudo('service dovecot restart')
  time.sleep(5)
  sudo('service apache2 restart')
  if fabtools.service.is_running('opendkim'):
    fabtools.service.restart('opendkim')
  else:
    fabtools.service.start('opendkim')


def credentials():
  run("clear")
  print(green("-----------------------------------------------------------------------------------"))
  print(green("URL Postfixadmin setup: http://{}:8080/postfixadmin/setup.php".format(domain)))
  print(green("URL Postfixadmin login: http://{}:8080/postfixadmin".format(domain)))
  print(green("-----------------------------------------------------------------------------------"))
  print(blue('SPF record for {} is "v=spf1 a mx -all"'.format(domain)))
  print(blue("-----------------------------------------------------------------------------------"))
  print(blue("Dkim record for {} is in /etc/postfix/dkim.txt".format(domain)))
  print(blue('When setting this up you should omit the "k=rsa; t=y;" portion of the value'))
  print(blue('So the value looks like this:"v=DKIM1; p=MIGfMA0GCSqGSIb3DQEBA..."'))
  print(blue("After adding Dkim record and update DNS check with command:"))
  print(red("dig dkim._domainkey.{} txt").format(domain))
  print(blue("-----------------------------------------------------------------------------------"))

  

def setup():
  common_setup()
  system_setup()
  configure_postfix()
  configure_dovecot()
  configure_apache()
  configure_mysql()
  configure_postfixadmin()
  configure_dkim()
  restart_services()
  credentials()
















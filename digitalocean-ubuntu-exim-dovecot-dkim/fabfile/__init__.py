# -*- coding: utf-8 -*-
# for Ubuntu 14.04
# installing exim + dovecot + dkim + script for mailboxes without sql

'''
how to run: fab -H demo.loc --user vagrant --password vagrant <command>

'''
import sys
from fabric.api import *
from fabtools import require
import fabtools
from unipath import Path
from fabric.contrib.files import upload_template
from jinja2 import *
from fabric.colors import blue, green, red
root = Path(__file__).ancestor(3)
print(root)
sys.path.append(root)
from worldevops import *

user = 'vagrant'
password = 'vagrant'
project = 'exim'
hostname = 'mail'
ip = '192.168.33.10'
domain = 'demo.loc'
commonname = 'mail.demo.loc'
env.local_root = Path(__file__).ancestor(2)
dovecot_path = '/etc/dovecot/conf.d/'

env.mailboxes = {
  'domain': domain,
  'MD5': "{{MD5}}",
  'info': genpass(),
  'admin': genpass(),
  'postmaster': genpass()
}

def common_setup():
    sudo('apt-get update')
    fabtools.require.deb.packages([
        'dovecot-core', 'dovecot-imapd', 'dovecot-pop3d', 'exim4-daemon-heavy', 'opendkim', 'opendkim-tools'
    ])

def system_setup():
	sudo('echo "{0} {1} www.{1} mail.{1}" >> /etc/hosts'.format(ip, domain))
	sudo('groupadd -g 120 -r vmail && useradd -g 120 -r -u 120 vmail && mkdir /home/vmail && chown vmail:vmail /home/vmail && chmod u=rwx,g=rx,o= /home/vmail')
	

def configure_dovecot_10_auth_conf():
	fabtools.require.file('{}10-auth.conf'.format(dovecot_path), """\
disable_plaintext_auth = no
auth_default_realm = {}
auth_mechanisms = plain login
!include auth-passwdfile.conf.ext
""".format(domain), use_sudo=True)


def configure_dovecot_auth_passwdfile_conf_ext():
	sudo('touch /etc/dovecot/passwd && chown root:dovecot /etc/dovecot/passwd && chmod u=rw,g=r,o= /etc/dovecot/passwd')
	fabtools.require.file('{}auth-passwdfile.conf.ext'.format(dovecot_path), """\

passdb {
  driver = passwd-file
  args = scheme=CRYPT username_format=%u /etc/dovecot/passwd
}

userdb {
  driver = passwd-file
  args = username_format=%u /etc/dovecot/passwd

default_fields = uid=vmail gid=vmail userdb_home=/home/vmail/%Ld/%Ln userdb_location=maildir:/home/vmail/%Ld/%Ln
}
""", use_sudo=True)


def configure_dovecot_10_logging_conf():
	fabtools.require.file('{}10-logging.conf'.format(dovecot_path), """\

log_timestamp = "%Y-%m-%d %H:%M:%S "
auth_verbose = no
auth_verbose_passwords = plain
auth_debug = no
mail_debug = no

""", use_sudo=True)


def configure_dovecot_10_mail_conf():
	fabtools.require.file('{}10-mail.conf'.format(dovecot_path), """\

mail_home = /home/vmail/%Ld/%Ln
mail_location = maildir:/home/vmail/%Ld/%Ln
mail_uid = vmail
mail_gid = vmail
first_valid_uid = 120
last_valid_uid = 120
first_valid_gid = 120
last_valid_gid = 120

""", use_sudo=True)
	
def configure_dovecot_10_master_conf():
	fabtools.require.file('{}10-master.conf'.format(dovecot_path), """\

service imap-login {
  inet_listener imap {
    #port = 143
  }
  inet_listener imaps {
    port = 993
    #ssl = yes
  }
}

service pop3-login {
  inet_listener pop3 {
    port = 110
  }
  inet_listener pop3s {
    #port = 995
    #ssl = yes
  }
}

service lmtp {
  unix_listener lmtp {
    #mode = 0666
  }
}

service auth {

  unix_listener auth-userdb {
    mode = 0666
    user = Debian-exim
    #group = 
  }

  unix_listener auth-client {
    mode = 0666
    user = Debian-exim
    #group = 
  }
}

""", use_sudo=True)	

def configure_dovecot_conf():
	fabtools.require.file('/etc/dovecot/dovecot.conf', """\

!include_try /usr/share/dovecot/protocols.d/*.protocol
listen = *
!include conf.d/*.conf
!include_try local.conf

""", use_sudo=True)

def configure_dovecot_15_maiboxes_conf():
	fabtools.require.file('/etc/dovecot/conf.d/15-mailboxes.conf', """\

##
## Mailbox definitions
##

# NOTE: Assumes "namespace inbox" has been defined in 10-mail.conf.
namespace inbox {
   inbox=yes

  #mailbox name {
    # auto=create will automatically create this mailbox.
    # auto=subscribe will both create and subscribe to the mailbox.
    #auto = no

    # Space separated list of IMAP SPECIAL-USE attributes as specified by
    # RFC 6154: \All \Archive \Drafts \Flagged \Junk \Sent \Trash
    #special_use =
  #}

  # These mailboxes are widely used and could perhaps be created automatically:
  mailbox Drafts {
    special_use = \Drafts
  }
  mailbox Junk {
    special_use = \Junk
  }
  mailbox Trash {
    special_use = \Trash
  }

  # For \Sent mailboxes there are two widely used names. We'll mark both of
  # them as \Sent. User typically deletes one of them if duplicates are created.
  mailbox Sent {
    special_use = \Sent
  }
  mailbox "Sent Messages" {
    special_use = \Sent
  }

  # If you have a virtual "All messages" mailbox:
  #mailbox virtual/All {
  #  special_use = \All
  #}

  # If you have a virtual "Flagged" mailbox:
  #mailbox virtual/Flagged {
  #  special_use = \Flagged
  #}
}

""", use_sudo=True)

def create_dovecot_init():
	fabtools.require.file('/etc/init.d/dovecot', """\

DAEMON=/usr/sbin/dovecot

# Uncomment to allow Dovecot daemons to produce core dumps.
#ulimit -c unlimited

test -x $DAEMON || exit 1
set -e

base_dir=`$DAEMON config -h base_dir`
pidfile=$base_dir/master.pid

if test -f $pidfile; then
  running=yes
else
  running=no
fi

case "$1" in
  start)
    echo -n "Starting Dovecot"
    $DAEMON
    echo "."
    ;;
  stop)
    if test $running = yes; then
      echo "Stopping Dovecot"
      kill `cat $pidfile`
      echo "."
    else
      echo "Dovecot is already stopped."
    fi
    ;;
  reload)
    if test $running = yes; then
      echo -n "Reloading Dovecot configuration"
      kill -HUP `cat $pidfile`
      echo "."
    else
      echo "Dovecot isn't running."
    fi
    ;;
  restart|force-reload)
    echo -n "Restarting Dovecot"
    if test $running = yes; then
      kill `cat $pidfile`
      sleep 1
    fi
    $DAEMON
    echo "."
    ;;
  *)
    echo "Usage: /etc/init.d/dovecot {start|stop|reload|restart|force-reload}" >&2
    exit 1
    ;;
esac

exit 0

""", use_sudo=True)
	sudo('chmod 755 /etc/init.d/dovecot')


def configure_dovecot():
	configure_dovecot_10_auth_conf()
	configure_dovecot_auth_passwdfile_conf_ext()
	configure_dovecot_10_logging_conf()
	configure_dovecot_10_mail_conf()
	configure_dovecot_10_master_conf()
	configure_dovecot_15_maiboxes_conf()
	configure_dovecot_conf()
	create_dovecot_init()
	sudo('service dovecot restart')

def configure_dkim():
	sudo('mkdir /etc/exim4/dkim')
	with cd ('/etc/exim4/dkim'):
		sudo('opendkim-genkey -D /etc/exim4/dkim/ -d {} -s mail'.format(domain))
		sudo('mv mail.private mail.{}.private'.format(domain))
		sudo('mv mail.txt mail.{}.public'.format(domain))
		sudo('chmod u=rw,g=r,o= * && chown root:Debian-exim *')

def configure_exim4_conf():
	fabtools.require.file('/etc/exim4/aliases', use_sudo=True)
	sudo('chown root:Debian-exim /etc/exim4/aliases')
	fabtools.require.file('/etc/exim4/local_domains', """ \
{}""".format(domain),use_sudo=True)

	tpldir = str(Path('etc', 'exim4'))
	target = str(Path('/', 'etc', 'exim4', 'exim4.conf'))
	context = {
		'domain': domain,
		'commonname': commonname
	}
	upload_template(
		filename="exim4.conf",
		destination=target,
		context=context,
		use_jinja=True,
		template_dir=tpldir,
		use_sudo=True
	)
	sudo('chmod u=rw,g=r,o= /etc/exim4/exim4.conf')
	sudo('chown root:Debian-exim /etc/exim4/exim4.conf')
	sudo('usermod -aG dovecot Debian-exim')
	sudo('/etc/init.d/exim4 reload')
	sudo('/etc/init.d/exim4 restart')

def script_mailboxes():
	fabtools.require.file('/home/{}/mailboxes.sh'.format(user), """\

#!/bin/sh

echo "1 - list of mailboxes"
echo "2 - add new mailbox"
echo "3 - delete exists mailbox"
echo "4 - add alias"
echo "Please enter number of action:"

read action

case $action in
     1)
          echo "This domain has next mailboxes:"
          ls -1 /home/vmail/{0}
          ;;
     2)
          echo "Enter username password"
          read mailuser pass
          if [ -d /home/vmail/{0}/$mailuser ]; then
            echo "This user already exists, please enter another name";
            exit;
          else
            hash=`doveadm pw -s MD5 -p $pass | sed 's/{{MD5}}//'`
            user=`echo $mailuser |cut -d'@' -f1`
            domain=`echo $mailuser |cut -d'@' -f2`
            mkdir -p /home/vmail/{0}/$user
            chown -R vmail:vmail /home/vmail/{0}/$user
            echo "$mailuser@{0}:$hash:120:120::/home/vmail/{0}/$user:" >> /etc/dovecot/passwd
          fi
          echo "Mailbox added"
          ;;
     3)
          echo "Enter username"
          read mailuser
          sed /$mailuser/d /etc/dovecot/passwd
          echo "Mailbox deleted from mailserver"
          echo "Please, remove directory of user from /home/vmail/{0} manually"
          ;; 
     4)
          echo "Enter aliasname mailbox1 mailbox2 ... up to 10 mailboxes"
          read alias mailbox1 mailbox2 mailbox3 mailbox4 mailbox5 mailbox6 mailbox7
mailbox8 mailbox9 mailbox10
          echo "$alias: $mailbox1@{0},$mailbox2@{0}",$mailbox3@{0},$mailbox4@{0},$mailbox5@{0},$mailbox6@{0},$mailbox7@{0},$mailbox8@{0},$mailbox9@{0},$mailbox10@{0} >> /etc/exim4/aliases
          echo "Alias added"
          ;;
     *)   echo "Unknown action"
          ;;
esac
exit

""".format(domain), use_sudo=True)
	sudo('chmod a+x /home/{}/mailboxes.sh'.format(user))

def add_default_mailboxes():
  fabtools.require.file('/home/{}/default_mailboxes.sh'.format(user), """\

#!/bin/sh

  mkdir -p /home/vmail/%(domain)s/info
  mkdir -p /home/vmail/%(domain)s/admin
  mkdir -p /home/vmail/%(domain)s/postmaster
  chown -R vmail:vmail /home/vmail/%(domain)s/info
  chown -R vmail:vmail /home/vmail/%(domain)s/admin
  chown -R vmail:vmail /home/vmail/%(domain)s/postmaster
  hash=`doveadm pw -s MD5 -p %(info)s | sed 's/{MD5}//'`
  hash1=`doveadm pw -s MD5 -p %(admin)s | sed 's/{MD5}//'`
  hash2=`doveadm pw -s MD5 -p %(postmaster)s | sed 's/{MD5}//'`
  echo "info@%(domain)s:$hash:120:120::/home/vmail/%(domain)s/info:" >> /etc/dovecot/passwd
  echo "admin@%(domain)s:$hash1:120:120::/home/vmail/%(domain)s/admin:" >> /etc/dovecot/passwd
  echo "postmaster@%(domain)s:$hash2:120:120::/home/vmail/%(domain)s/postmaster:" >> /etc/dovecot/passwd

  """ % env.mailboxes, use_sudo=True)
  sudo('chmod a+x /home/{}/default_mailboxes.sh'.format(user))
  sudo('/bin/sh /home/{}/default_mailboxes.sh'.format(user))
  sudo('rm /home/{}/default_mailboxes.sh'.format(user))

  run("clear")
  print(green("-----------------------------------------------------------------------------------"))
  print(green("created mailbox info@%(domain)s  with password: %(info)s" % env.mailboxes))
  print(green("created mailbox admin@%(domain)s with password: %(admin)s" % env.mailboxes))
  print(green("created mailbox postmaster@%(domain)s with password: %(postmaster)s" % env.mailboxes))
  print(green("-----------------------------------------------------------------------------------"))

def setup_cronjobs():
    fabtools.cron.add_task('eximlogs', '0 0 */3 * *', 'root',
                           'find /var/log/exim4 -type f -mtime +3 -print0 | xargs -0 rm -f', use_sudo=True)

def setup():
	common_setup()
	system_setup()
	setup_fail2ban_ssh()
	configure_dovecot()
	configure_dkim()
	configure_exim4_conf()
	script_mailboxes()
	add_default_mailboxes()
  setup_cronjobs()














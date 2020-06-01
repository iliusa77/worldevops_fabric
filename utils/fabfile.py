import os
from fabric.api import *
from unipath import Path
from contextlib import contextmanager
from fabric.contrib.files import upload_template
from fabric.api import settings
from fabric.colors import green
import fabtools


def vagrant():
    env.hosts = ['demo.loc']
    env.user = 'vagrant'
    env.password = 'vagrant'


def worldevops():
    env.user = 'worldevops'
    env.password = 'worldevops'


def destroy_apache():
    fabtools.service.stop('apache2')
    fabtools.deb.uninstall(['apache2'], purge=True, options=None)
    sudo('rm -f /etc/apache2/sites-available/*')
    sudo('rm -f /etc/apache2/sites-enabled/*')
    # sudo('apt-get purge apache2*')


def destroy_nginx():
    fabtools.service.stop('nginx')
    fabtools.deb.uninstall(['nginx'], purge=True, options=None)
    sudo('rm -f /etc/nginx/sites-available/*')
    sudo('rm -f /etc/nginx/sites-enabled/*')


def destroy_supervisor():
    fabtools.service.stop('supervisor')
    fabtools.deb.uninstall(['supervisor'], purge=True, options=None)
    sudo('apt-get purge supervisor*')
    # sudo('apt-get -y  remove supervisor')
    # sudo('apt-get -y  --purge remove supervisor\*')


class FabricException(Exception):
    pass


def destroy_all():
    with settings(abort_exception=FabricException):
        try:
            destroy_supervisor()
        except FabricException:
            pass
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

    with settings(abort_exception=FabricException):
        try:
            destroy_apache()
        except FabricException:
            pass
    sudo('rm -rf %s' % env.projects_dir)


def destroy_mysql():
    with settings(abort_exception=FabricException):
        try:
            sudo('service mysql stop')  #or mysqld
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


def destroy_postgresql():
    with settings(abort_exception=FabricException):
        try:
            sudo('service postgresql stop')
            sudo('killall psql')
        except FabricException:
            pass
    sudo('apt-get -y --purge autoremove postgresql postgresql-*')
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

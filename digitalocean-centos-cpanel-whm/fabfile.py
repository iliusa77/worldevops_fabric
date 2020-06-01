import os
from fabric.api import task, run, env, settings, cd, sudo, prefix, put
from fabric.contrib.files import upload_template
import fabtools
from fabric.contrib import files
from contextlib import contextmanager
from unipath import Path

def setup():
	sudo('yum -y install perl && hostnamectl set-hostname cpanel.try.direct')
	sudo('cd /home && curl -o latest -L https://securedownloads.cpanel.net/latest && sh latest')
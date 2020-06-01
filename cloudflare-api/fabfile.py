#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
export CLOUDFLARE_API_KEY=''
run: fab -H localhost setup

'''

import CloudFlare  # sudo pip install CloudFlare
import time
import os
from fabric.api import *
from unipath import Path

if 'WORLDEVOPS_PATH' not in os.environ:
    raise Exception("WORLDEVOPS_PATH is not set. add export WORLDEVOPS_PATH='/home/user/devops_fabric' in ~/.bashrc")
# for solving "WORLDEVOPS_PATH is not set." add export WORLDEVOPS_PATH='/home/user/devops_fabric' in ~/.bashrc

source = Path(os.environ.get('WORLDEVOPS_PATH'), 'cloudflare-api', 'python-cloudflare')
token = os.environ['CLOUDFLARE_API_KEY']  # Cloudflare api key
email = 'admin@worldevops.online'

cfapi = None


def setup():
    with cd(source):
        sudo('python setup.py install')


def config():
    with cd(source):
        from cloudflare import CloudFlare
        global cfapi
        cfapi = CloudFlare(email, token)


# Load all zones
# fab -H localhost zone_load_multi
def zone_load_multi():
    if not cfapi:
        config()
    show = cfapi.zone_load_multi()
    print(show)


# Create new DNS Record
# fab -H localhost --set=domain='demo.loc',type='A',subdomain='sub1',ip='1.2.3.4' rec_new
def rec_new():
    if not cfapi:
        config()
    cfapi.rec_new(env.domain, env.type, env.subdomain, env.ip)


# Get id DNS record by name
# fab -H localhost --set=domain='demo.loc',subdomain='sub1' get_rec_id_by_name
def get_rec_id_by_name():
    if not cfapi:
        config()
    show = cfapi.get_rec_id_by_name(env.domain, env.subdomain)
    print(show)

    # Edit an existing record
    # fab -H localhost --set=domain='demo.loc',type='A',rec_id='626801038',subdomain='sub2',ip='1.2.3.4',service_mode='0',ttl='1' rec_edit


def rec_edit():
    if not cfapi:
        config()
    cfapi.rec_edit(env.domain, env.type, env.rec_id, env.subdomain, env.ip, env.service_mode, env.ttl)


# Delete DNS record
# fab -H localhost --set=domain='demo.loc',rec_id='626781850' rec_delete
def rec_delete():
    if not cfapi:
        config()
    cfapi.rec_delete(env.domain, env.rec_id)

# more functions there are in ~/hourlies/cloudflare-api/python-cloudflare/cloudflare/__init__.py


# Create new DNS Record with curl
# fab -H localhost --set=domain='demo.loc',subdomain='sub1',ip='1.2.3.4' curl_add_rec
def curl_add_rec():
    run("curl https://www.cloudflare.com/api_json.html \
  -d 'a=rec_new' \
  -d 'tkn={0}' \
  -d 'email={1}' \
  -d 'z={2}' \
  -d 'type=A' \
  -d 'name={3}' \
  -d 'content={4}' \
  -d 'ttl=120'".format(token, email, env.domain, env.subdomain, env.ip))

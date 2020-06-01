#!/usr/bin/env python
# -*- coding: utf-8 -*-

import digitalocean
import time
import os

token = os.environ['DIGITALOCEAN_API_KEY']  # digital ocean api token

user = 'client'  # master user, owner of the application
domain = 'mythings.space'


def create_droplet(domain):
    droplet = digitalocean.Droplet(
        token=token,
        name=domain,
        region='nyc3',  # New York 3
        image=os.environ['DIGITALOCEAN_DEFAULT_IMAGE'],
        size_slug='512mb',  # 512MB
        backups=False
    )
    droplet.create()
    actions = droplet.get_actions()
    status = ''
    while True:
        for action in actions:
            action.load()
            # Once it shows complete, droplet is up and running
            status = action.status
            print('Droplet creating status .. ' + status)
            if status == 'completed':
                break
        if status == 'completed':
            break
        else:
            time.sleep(2)
    return droplet


def droplets():
    manager = digitalocean.Manager(token=token)
    droplets = manager.get_all_droplets()
    for droplet in droplets:
        print(droplet.ip_address)
        print(droplet.name)
        print("\n")


def genpass():
    from random import choice
    import string
    return ''.join(choice(string.letters + string.digits) for _ in range(8))


if __name__ == '__main__':
    droplet = create_droplet(domain)
    print('Droplet created')
    while not droplet.ip_address:
        print('droplet has no ip assigned yet')
        time.sleep(2)
        droplet.load()

    while not droplet.status == 'active':
        droplet.get_actions()
        droplet.load()
        print('current status .. ' + droplet.status)
        print('waiting for ssh connect..')
        time.sleep(2)

    time.sleep(5)
    os.system('ssh -oStrictHostKeyChecking=no {0}@{1} uptime'.format('worldevops', droplet.ip_address))

    passwd = genpass()
    command = 'fab --user=worldevops -H {host} create_app_user:{user},passwd={passwd}'.format(
        host=droplet.ip_address, user=user, passwd=passwd
    )
    os.system(command)
    print(command)

    command = 'fab -H {host} --user={user} --password={passwd} setup'.format(
        host=droplet.ip_address, passwd=passwd, user=user
    )
    print(command)
    os.system(command)

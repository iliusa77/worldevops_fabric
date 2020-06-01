#This script will create instance in Amazon AWS EC2 and install app from worldevops repository

#install awscli
#sudo pip install awscli

#configure aws credentials
'''
aws configure
AWS Access Key ID [None]: AKIAI***********A
AWS Secret Access Key [None]: cWkwvOBrsS****************b
Default region name [None]: us-west-2
Default output format [None]:
'''
#run this script
'''
python install.py
No hosts found. Please specify (single) host string for connection: localhost
[localhost] out: sudo password:
enter your sudo pass
'''

from fabtools.python import virtualenv
from fabric.api import cd, run, sudo, task, get, put, settings
import os, time
from unipath import Path
if  'WORLDEVOPS_PATH' not in os.environ:
    raise Exception("WORLDEVOPS_PATH is not set. add export WORLDEVOPS_PATH='/your_path_to_worldevops' in ~/.bashrc")
# for solving "WORLDEVOPS_PATH is not set." add export WORLDEVOPS_PATH='/your_path_to_worldevops' in ~/.bashrc 

class FabricException(Exception):
    pass

instance_type = 't2.micro'
ami_ubuntu14 = 'ami-01f05461'
ami_ubuntu16 = 'ami-a9d276c9'
security_group1 = 'allowssh'
security_group2 = 'allowhttp'
security_group3 = 'allow-22-and-80'
#key_name = 'worldevops'
product = 'digitalocean-ubuntu-suitecrm'
project = 'test'
domain = 'demo.loc'
key_name2 = project


def install_aws_cli():
	sudo('apt-get update && apt-get install python-pip')
	sudo('pip install awscli')

def create_key():
	with cd('/home/devadmin/hourlies/aws-awscli'):
		run("aws ec2 create-key-pair --key-name {0} --query 'KeyMaterial' --output text > {0}.pem".format(key_name2))
		run("chmod 400 {0}.pem".format(key_name2))

def check_instance_ready(host):
	target = Path(os.environ.get('HOURLIES_PATH'), project)
	with settings(abort_exception=FabricException):
		try:
			with cd(Path(target, product)):
				time.sleep(15)
				run('fab -H {0} --user ubuntu -i "{1}.pem" --set=domain={2},project={3} -- uname -a'.format(host, key_name2, domain, project))
		except FabricException:
			check_instance_ready(host)
		print("connected success")
		return True


def setup():
	source0 = Path(os.environ.get('WORLDEVOPS_PATH'))
	source = Path(os.environ.get('WORLDEVOPS_PATH'), product)
	target = Path(os.environ.get('WORLDEVOPS_PATH'), project)
	run('mkdir {}'.format(target))
	run('cp -r {0} {1}'.format(source, target))
	run('cp {0}/worldevops.py {1}'.format(source0, target))
	sudo('cp /home/devadmin/hourlies/aws-awscli/{0}.pem {1}/{2}'.format(key_name2, target, product))
	with cd(Path(target, product)):
		instance_id = run("aws ec2 run-instances --image-id {0} --security-group-ids \
		{1} --count 1 --instance-type {2} --key-name {3} --query 'Instances[0].InstanceId'".format(ami_ubuntu14, security_group3, instance_type, key_name2))
		print(instance_id)
		if instance_id:
			host = run("aws ec2 describe-instances --instance-ids {} --query 'Reservations[0].Instances[0].PublicIpAddress'".format(instance_id))
			print(host)
			if check_instance_ready(host):
				run('fab -H {0} --user ubuntu -i "{1}.pem" \
				--set=domain={2},project={3},http_server=nginx setup'.format(host, key_name2, domain, project))

if __name__ == '__main__':
	install_aws_cli()
	create_key()
	print('Key created and named {}.pem'.format(key_name2))
	setup()

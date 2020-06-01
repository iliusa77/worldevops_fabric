Command sequence for testing in vagrant:

fab -H demo.loc --user vagrant --password vagrant --set=domain=demo.loc,ip=192.168.33.10 create_app_user:redmine,redmine
fab -H demo.loc --user redmine --password redmine --set=domain=demo.loc,ip=192.168.33.10 setup

Command sequence for production systems :
1. Create a user on remote system with public_key and sudo priveleges

fab -H {host_ip} --user {user}  --set=domain={prefered_domain},ip=192.168.33.10 create_app_user:redmine,redmine
fab -H {host_ip} --user redmine --password redmine --set=domain={prefered_domain},ip=192.168.33.10 setup

2. Change redmine password and remove users from sudoers

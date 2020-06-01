install.py executes two methods:

fab -H {host} --user=worldevops --set=domain={domain} create_app_user:{user},passwd={passwd}
fab -H {host} --user={user} --set=domain={domain} --password={passwd} setup_with_nginx

Can be used separately, but you should have or generate password for second user

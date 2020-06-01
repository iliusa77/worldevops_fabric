
#!/bin/bash

sudo adduser --system --home=/opt/openerp --group openerp;
sudo apt-get install postgresql -y;
sudo su - postgres;
createuser --createdb --username postgres --no-createrole --no-superuser --pwprompt openerp

sudo apt-get install python-docutils -y;
sudo apt-get install python-gdata -y;
sudo apt-get install python-mako -y;
sudo apt-get install python-dateutil -y;
sudo apt-get install python-lxml -y;
sudo apt-get install python-libxslt1 -y;
sudo apt-get install python-ldap -y;
sudo apt-get install python-reportlab -y;
sudo apt-get install python-pybabel -y;
sudo apt-get install python-pychart -y;
sudo apt-get install python-openid -y;
sudo apt-get install python-simplejson -y;
sudo apt-get install python-psycopg2 -y;
sudo apt-get install python-vobject -y;
sudo apt-get install python-vatnumber -y;
sudo apt-get install python-webdav -y;
sudo apt-get install python-xlwt -y;
sudo apt-get install python-yaml -y;
sudo apt-get install python-zsi -y;

sudo wget -O - https://nightly.odoo.com/odoo.key | apt-key add -;
sudo echo "deb http://nightly.odoo.com/7.0/nightly/deb/ ./" >> /etc/apt/sources.list;
sudo apt-get update && sudo apt-get install openerp -y;

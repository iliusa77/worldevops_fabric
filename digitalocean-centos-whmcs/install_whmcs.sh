#!/bin/bash
#This script install WHMCS 6.3 to CentOS 7

# check system requirements for WHMCS to http://docs.whmcs.com/System_Requirements

#Installation LAMP

rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY*;
yum -y install epel-release;
yum -y install mariadb-server mariadb;
systemctl start mariadb.service && systemctl enable mariadb.service;
mysql_secure_installation;
yum -y install httpd;
systemctl start httpd.service && systemctl enable httpd.service;
firewall-cmd --permanent --zone=public --add-service=http ;

#for php 5.6
rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm;
rpm -Uvh https://mirror.webtatic.com/yum/el7/webtatic-release.rpm;
yum install php56w php56w-gd php56w-pdo php56w-mysql curl curl-devel unzip wget;
echo "date.timezone = Europe/Amsterdam" >> /etc/php.ini;
systemctl restart httpd.service;

#for php 5.4
#yum -y install php-mysql
#yum -y install php-gd php-ldap php-odbc php-pear php-xml php-xmlrpc php-mbstring php-snmp php-soap curl curl-devel unzip wget
#echo "date.timezone = Europe/Amsterdam" >> /etc/php.ini
#systemctl restart httpd.service


#Installation Ioncube

cd /tmp;
wget http://downloads3.ioncube.com/loader_downloads/ioncube_loaders_lin_x86-64.tar.gz;
tar -xvf ioncube_loaders_lin_x86-64.tar.gz

#ls ioncube/
#ioncube_loader_lin_4.1.so     ioncube_loader_lin_5.0_ts.so  ioncube_loader_lin_5.4.so     loader-wizard.php
#ioncube_loader_lin_4.2.so     ioncube_loader_lin_5.1.so     ioncube_loader_lin_5.4_ts.so  README.txt
#ioncube_loader_lin_4.3.so     ioncube_loader_lin_5.1_ts.so  ioncube_loader_lin_5.5.so     USER-GUIDE.pdf
#ioncube_loader_lin_4.3_ts.so  ioncube_loader_lin_5.2.so     ioncube_loader_lin_5.5_ts.so  USER-GUIDE.txt
#ioncube_loader_lin_4.4.so     ioncube_loader_lin_5.2_ts.so  ioncube_loader_lin_5.6.so
#ioncube_loader_lin_4.4_ts.so  ioncube_loader_lin_5.3.so     ioncube_loader_lin_5.6_ts.so
#ioncube_loader_lin_5.0.so     ioncube_loader_lin_5.3_ts.so  LICENSE.txt

#for php 5.6
#php -v
#PHP 5.6.23 (cli) (built: Jun 23 2016 18:38:35


#php -i | grep extension_dir
#extension_dir => /usr/lib64/php/modules => /usr/lib64/php/modules

cp ioncube/ioncube_loader_lin_5.6.so /usr/lib64/php/modules/;
echo "zend_extension = /usr/lib64/php/modules/ioncube_loader_lin_5.6.so" >> /etc/php.ini;
systemctl restart httpd.service;

#for php 5.4
#php -v
#PHP 5.4.27

#php -i | grep extension_dir
#extension_dir => /usr/lib64/php/modules => /usr/lib64/php/modules

cp ioncube/ioncube_loader_lin_5.4.so /usr/lib64/php/modules/;
echo "zend_extension = /usr/lib64/php/modules/ioncube_loader_lin_5.4.so" >> /etc/php.ini;
systemctl restart httpd.service;

#create database whmcs;
mysql -u root -pvagrant -h localhost -e 'CREATE DATABASE whmcs;';
#create dbuser whmcs;
mysql -u root -pvagrant -h localhost -e 'CREATE USER whmcs@localhost IDENTIFIED BY 'VPe6NH[';';
#create PRIVILEGES
mysql -u root -pvagrant -h localhost -e 'GRANT ALL PRIVILEGES ON  *.* to 'whmcs'@'localhost' WITH GRANT OPTION;';


#Installation WHMCS

#disable selinux
sed -i 's/SELINUX=Enforcing/SELINUX=Disabled/' /etc/sysconfig/selinux;
shutdown -r now;     


#download WHMCS 6.3 from https://mega.nz/#!gRJyWYJJ!SwwR8FLhuYNtVOHhHpkqxSoSn5wOQDVeIg6kHIgg2Ew
cd /var/www/html && rm -rf .;
cp ./whmcs-v630-nulled-by-mecho.network.zip /var/www/html;

unzip whmcs-v630-nulled-by-mecho.network.zip;

mv whmcs-v630-nulled-by-mecho.network/* . && rm -rf whmcs-v630-nulled-by-mecho.network/;

cp configuration.php.new configuration.php;
chmod 777 configuration.php;
chmod -R 777 attachments/;
chmod -R 777 templates_c/;
chmod -R 777 downloads/;

#open url http://192.168.33.10/install/install.php for installation WHMCS
#install WHMCS with dbuser='whmcs' dbpassword='VPe6NH[' dbname='whmcs'
#delete folder /var/www/html/install and open url http://192.168.33.10/admin/index.php

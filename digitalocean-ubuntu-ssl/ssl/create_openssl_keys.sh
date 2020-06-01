#!/bin/bash


#Required
domain=$1
commonname=$domain
 
#Change to your company details
country=GB
state=Nottingham
locality=Nottinghamshire
organization=Jamescoyle.net
organizationalunit=IT
email=administrator@jamescoyle.net
 

#Generation of certificates

mkdir /open-ssl-keys && cd /open-ssl-keys
openssl genrsa -out rootCA.key 2048
openssl req -x509 -new -key rootCA.key -days 10000 -out rootCA.crt \
    -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email"

openssl genrsa -out $domain.key 2048
openssl req -new -key $domain.key -out $domain.csr \
    -subj "/C=$country/ST=$state/L=$locality/O=$organization/OU=$organizationalunit/CN=$commonname/emailAddress=$email" 

openssl x509 -req -in $domain.csr -CA rootCA.crt -CAkey rootCA.key -CAcreateserial -out $domain.crt -days 5000




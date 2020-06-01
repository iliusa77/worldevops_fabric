#!/bin/bash
mysql -u root -e "CREATE DATABASE akeneo_pim;";
mysql -u root -e "GRANT ALL PRIVILEGES ON akeneo_pim.* TO akeneo_pim@localhost IDENTIFIED BY 'akeneo_pim';";

<?php

/*
 +-----------------------------------------------------------------------+
 | Local configuration for the Roundcube Webmail installation.           |
 |                                                                       |
 | This is a sample configuration file only containing the minimum       |
 | setup required for a functional installation. Copy more options       |
 | from defaults.inc.php to this file to override the defaults.          |
 |                                                                       |
 | This file is part of the Roundcube Webmail client                     |
 | Copyright (C) 2005-2013, The Roundcube Dev Team                       |
 |                                                                       |
 | Licensed under the GNU General Public License version 3 or            |
 | any later version with exceptions for skins & plugins.                |
 | See the README file for a full license statement.                     |
 +-----------------------------------------------------------------------+
*/

$config = array();


$config['db_dsnw'] = '%(db_type)s://%(db_user)s:%(db_pass)s@localhost/%(db_name)s';

$config['default_host'] = 'localhost';

$config['smtp_server'] = '';

$config['smtp_port'] = 25;

$config['smtp_user'] = '';

$config['smtp_pass'] = '';

$config['support_url'] = '';

$config['product_name'] = 'Roundcube Webmail';

$config['des_key'] = 'rcmail-!24ByteDESkey*Str';

$config['plugins'] = array(
    'archive',
    'zipdownload',
);

$config['skin'] = 'larry';


$config['drafts_mbox'] = 'INBOX.Drafts';
$config['junk_mbox'] = 'INBOX.Junk';
$config['sent_mbox'] = 'INBOX.Sent';
$config['trash_mbox'] = 'INBOX.Trash';
$config['default_folders'] = array('INBOX', 'INBOX.Drafts', 'INBOX.Sent', 'INBOX.Junk', 'INBOX.Trash');
$config['create_default_folders'] = true;
<?php
    define('DB_NAME', '%(name)s');
    define('DB_USER', '%(user)s');
    define('DB_PASSWORD', '%(pass)s');
    define('DB_HOST', 'localhost');
    define('DB_CHARSET', 'utf8mb4');
    define('DB_COLLATE', '');

    define('AUTH_KEY',         '%(AUTH_KEY)s');
    define('SECURE_AUTH_KEY',  '%(SECURE_AUTH_KEY)s');
    define('LOGGED_IN_KEY',    '%(LOGGED_IN_KEY)s');
    define('NONCE_KEY',        '%(NONCE_KEY)s');
    define('AUTH_SALT',        '%(AUTH_SALT)s');
    define('SECURE_AUTH_SALT', '%(SECURE_AUTH_SALT)s');
    define('LOGGED_IN_SALT',   '%(LOGGED_IN_SALT)s');
    define('NONCE_SALT',       '%(NONCE_SALT)s');

    $table_prefix  = 'wp_';

    define('WP_DEBUG', false);

    if ( !defined('ABSPATH') )
        define('ABSPATH', dirname(__FILE__) . '/');

    require_once(ABSPATH . 'wp-settings.php');
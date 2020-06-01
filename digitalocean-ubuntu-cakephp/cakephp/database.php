<?php
class DATABASE_CONFIG {

	public $default = array(
		'datasource' => 'Database/Mysql',
		'persistent' => false,
		'host' => 'localhost',
		'login' => '%(user)s',
		'password' => '%(password)s',
		'database' => '%(name)s',
		'prefix' => '',
		//'encoding' => 'utf8',
	);

	public $test = array(
		'datasource' => 'Database/Mysql',
		'persistent' => false,
		'host' => 'localhost',
		'login' => '%(user)s',
		'password' => '%(password)s',
		'database' => '%(name)s',
		'prefix' => '',
		//'encoding' => 'utf8',
	);
}
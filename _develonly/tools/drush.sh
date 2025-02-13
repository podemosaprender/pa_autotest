#!/usr/bin/bash

PHP=${PHP:-`which php74`}
PHP=${PHP:-`which php73`}
PHP=${PHP:-`which php72`}

if ! [ -f ~/bin/drush.phar ]; then
	wget https://github.com/drush-ops/drush/releases/download/8.5.0/drush.phar
	chmod u+x ~/bin/drush.phar
fi

echo "RUNNING $PHP ~/bin/drush.phar $*"

$PHP ~/bin/drush.phar $*



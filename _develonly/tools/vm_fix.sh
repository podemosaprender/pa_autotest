#!/usr/bin/bash
#INFO: run in VM to fix minor config details

DIR=`dirname $0`
echo "MY DIR=$DIR"
crontab $DIR/vm.crontab

ln -s /var/www/drupal/web ~/web
mkdir -p ~/logs
ln -s /var/log/apache2 ~/logs/apache2
ln -s /var/log/php8.2-fpm.log ~/logs/php8.2-fpm.log
ln -s /var/log/php7.4-fpm.log ~/logs/php7.4-fpm.log
sudo chmod ug+x /var/www/drupal/web/scripts/*sh
sudo chmod -R a+r /var/log/apache2
sudo chmod  a+x /var/log/apache2
sudo chmod a+r ~/logs/

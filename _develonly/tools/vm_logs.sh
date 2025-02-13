#!/usr/bin/bash
#INFO: make sure logs can be accessed in pausr home

sudo chmod -R a+rw /var/log/apache2 /var/log/php*
sudo chmod  a+x /var/log/apache2
mkdir -p ~/logs
cd ~/logs
for i in /var/log/apache2 /var/log/php* ; do ln -sf $i . ; done
ls ~/logs

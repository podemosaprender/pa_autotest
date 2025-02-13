#!/usr/bin/bash
#INFO: enable remote access to jupyter, vnc, etc.

MY_DIR=`dirname $0`

if [ -z "$P_VM_USR" ]; echo "export P_VM_USR=my_pa_vm_usr@vmX.make.podemosaprender.org #ASK: for user and keys!"; exit 1; fi
if [ -z "$P_VM_PORT1" ]; echo "export P_VM_PORT1=112233 #ASK: for ports!"; exit 1; fi
if [ -z "$P_VM_PORT2" ]; echo "export P_VM_PORT2=3344 #ASK: for ports!"; exit 1; fi

echo "**WARNING** ensure this vm has NO access to your disk, machines in your network, etc!"
echo "write YES to proceed"
read R

if [ "$R" != "YES" ]; then
	echo "ABORTED by user"
	exit
fi

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT #A:kill all bg on exit

sudo a2enmod proxy_http                                                                                                       
sudo a2enmod proxy_wstunnel                                                                                                   
sudo a2enmod auth_basic                                                                                                       
sudo apt install autossh                                                                                                      
sudo cp -r $MY_DIR/vm_conf/apache2/auth /etc/apache2
sudo cp -r $MY_DIR/vm_conf/apache2/php7-vm-proxy.conf /etc/apache2/sites-available
sudo a2dissite php7
sudo a2ensite php7-vm-proxy
sudo apachectl restart

KEY='~/.ssh/id_rsa'
if [ -f "~/.ssh/$P_VM_USR" ]; then KEY="~/.ssh/$P_VM_USR"; fi
autossh -M 0 -N -o "ServerAliveInterval 10" -o "ServerAliveCountMax 3" -R $P_VM_PORT1:localhost:10087 -R $P_VM_PORT2:localhost:8000 -T -N -i $KEY $P_VM_USR & 

$MY_DIR/vm_test_jupyter.sh


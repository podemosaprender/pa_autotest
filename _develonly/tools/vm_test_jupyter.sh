#!/usr/bin/bash
#INFO: launch jupyter server for test development

MY_DIR=`dirname $0`

trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT #A:kill all bg on exit

if ! [ -d ~/3p/noVNC ]; then
	(mkdir -p ~/3p/; cd ~/3p/ ; git clone https://github.com/novnc/noVNC.git )
fi

export XAUTHLOCALHOSTNAME=localhost
export DISPLAY=:99
Xvfb -auth ~/.Xauthority -ac -br -screen 0 1920x950x16 $DISPLAY &
sleep 3
touch ~/.Xauthority
xauth generate $DISPLAY . trusted 

x11vnc -display $DISPLAY -auth gess --forever --passwd 'NoLoRompo' --shared &
sleep 3
(cd ~/3p/noVNC/ ; utils/novnc_proxy ) &
#A: screen server

AUTOTEST_DIR=$MY_DIR/../autotest
cd $AUTOTEST_DIR

if ! [ -d ~/venvs/selenium ]; then
	mkdir -p ~/venvs
	python -mvenv ~/venvs/selenium
	. ~/venvs/selenium/bin/activate
	tools/install
	pip install jupyterlab
fi

. ~/venvs/selenium/bin/activate
export P_VISIBLE=1
export PYTHONPATH=$AUTOTEST_DIR:$PYTHONPATH
PASS=`python -c "from jupyter_server.auth import passwd; print(passwd('NoLoRompo'))"`; jupyter-lab --no-browser -y --port 8000 --ip=0.0.0.0 --ServerApp.password="$PASS" 

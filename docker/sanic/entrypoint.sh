#!/usr/bin/env sh
set -e

if [ -f /home/site/wwwroot/app/main.py ]; then
    DEFAULT_MODULE_NAME=app.main
elif [ -f /home/site/wwwroot/main.py ]; then
    DEFAULT_MODULE_NAME=main
fi
MODULE_NAME=${MODULE_NAME:-$DEFAULT_MODULE_NAME}
VARIABLE_NAME=${VARIABLE_NAME:-app}
export APP_MODULE=${APP_MODULE:-"$MODULE_NAME:$VARIABLE_NAME"}

if [ -f /home/site/wwwroot/gunicorn_conf.py ]; then
    DEFAULT_GUNICORN_CONF=/home/site/wwwroot/gunicorn_conf.py
elif [ -f /home/site/wwwroot/app/gunicorn_conf.py ]; then
    DEFAULT_GUNICORN_CONF=/home/site/wwwroot/app/gunicorn_conf.py
else
    DEFAULT_GUNICORN_CONF=/gunicorn_conf.py
fi
export GUNICORN_CONF=${GUNICORN_CONF:-$DEFAULT_GUNICORN_CONF}




cat >/etc/motd <<EOL 

  _____                               
  /  _  \ __________ _________   ____  
 /  /_\  \\___   /  |  \_  __ \_/ __ \ 
/    |    \/    /|  |  /|  | \/\  ___/ 
\____|__  /_____ \____/ |__|    \___  >
        \/      \/                  \/ 

A P P   S E R V I C E   O N   L I N U X

Documentation: http://aka.ms/webapp-linux

EOL
cat /etc/motd

service ssh start


# Get environment variables to show up in SSH session
eval $(printenv | awk -F= '{print "export " $1"="$2 }' >> /etc/profile)

exec "$@"
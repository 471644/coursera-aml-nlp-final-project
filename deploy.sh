#!/bin/bash
 
 BCyan='\033[1;36m'
 NC='\033[0m'
 
 echo "${BCyan}Creating swapfile...${NC}"
 sudo dd if=/dev/zero of=/swapfile bs=1MB count=1200
 sudo chown root:root /swapfile
 sudo chmod 0600 /swapfile
 sudo mkswap /swapfile
 sudo swapon /swapfile
 
 echo "${BCyan}Installing python dependencies...${NC}"
 sudo pip3 install -U pip
 sudo pip3 --no-cache-dir install -r requirements.txt
 
 echo "${BCyan}Converting embeddings to shelve format...${NC}"
 python3 convert_embeddings.py
 
 echo "${BCyan}Enter Telegram Bot API token:${NC}"
 read TELEGRAM_TOKEN
 
 echo "${BCyan}Creating service...${NC}"
 cat > telegram_bot << EOF
#!/bin/sh
# kFreeBSD do not accept scripts as interpreters, using #!/bin/sh and sourcing.
if [ true != "$INIT_D_SCRIPT_SOURCED" ] ; then
    set "$0" "$@"; INIT_D_SCRIPT_SOURCED=true . /lib/init/init-d-script
fi
### BEGIN INIT INFO
# Provides:          telegram_bot
# Required-Start:    $remote_fs $syslog
# Required-Stop:     $remote_fs $syslog
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: Stack Overflow assistant and chit-chat bot for Telegram
### END INIT INFO

# Author: Georgy Ignatov <vBLFTePebWNi6c@gmail.com>

DESC="Stack Overflow assistant and chit-chat bot for Telegram"
DAEMON="python3 $(pwd)/main_bot.py --token $TELEGRAM_TOKEN"
EOF

sudo mv telegram_bot /etc/init.d
sudo chmod +x /etc/init.d/telegram_bot
sudo update-rc.d telegram_bot defaults

 echo "${BCyan}Completed successfully.${NC}"

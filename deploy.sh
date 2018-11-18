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
 
 cat > start_telegram_bot.sh << EOF
#!/bin/bash
python3 $(pwd)/main_bot.py --token $TELEGRAM_TOKEN
EOF

 cat > telegram_bot << EOF
#!/bin/bash
tmux new-session -d -s "telegram_bot" $(pwd)/start_telegram_bot.sh
EOF

sudo mv telegram_bot /etc/init.d
sudo chmod +x /etc/init.d/telegram_bot
sudo update-rc.d telegram_bot defaults

 echo "${BCyan}Completed successfully.${NC}"

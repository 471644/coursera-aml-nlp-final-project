#!/bin/bash
 
 BCyan='\033[1;36m'
 
 echo -e "${BCyan}Creating swapfile..."
 sudo dd if=/dev/zero of=/swapfile bs=1MB count=1200
 sudo chown root:root /swapfile
 sudo chmod 0600 /swapfile
 sudo mkswap /swapfile
 sudo swapon /swapfile
 
 echo -e "${BCyan}Installing python dependencies..."
 sudo pip3 install -U pip
 sudo pip3 --no-cache-dir install -r requirements.txt
 
 echo -e "${BCyan}Converting embeddings to shelve format..."
 python3 convert_embeddings.py
 
 echo -e "${BCyan}Enter Telegram Bot API token:"
 read TELEGRAM_TOKEN
 
 echo -e "${BCyan}Creating startup script..."
 cat > telegram_bot << EOF
#!/bin/bash
tmux new -s telegram_bot
python3 $(pwd)/main_bot.py --token $TELEGRAM_TOKEN
tmux detach
EOF

sudo mv telegram_bot /etc/init.d
sudo chmod +x /etc/init.d/telegram_bot
sudo update-rc.d telegram_bot defaults

 echo -e "${BCyan}Completed successfully."

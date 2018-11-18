#!/bin/bash
 
 echo "Create swapfile..."
 sudo dd if=/dev/zero of=/swapfile bs=1MB count=1200
 sudo chown root:root /swapfile
 sudo chmod 0600 /swapfile
 sudo mkswap /swapfile
 sudo swapon /swapfile
 
 echo "Install python dependencies..."
 sudo pip3 install -U pip
 sudo pip3 --no-cache-dir install -r requirements.txt
 
 echo "Convert embeddings to shelve format..."
 python3 convert_embeddings.py
 
 echo "Enter Telegram Bot API token:"
 read TELEGRAM_TOKEN
 
 echo "Create startup script..."
 cat > start_telegram_bot.sh << EOF
#!/bin/bash
tmux new -s telegram_bot
python3 $(pwd)/main_bot.py --token $TELEGRAM_TOKEN
tmux detach
EOF

sudo mv start_telegram_bot.sh /etc/init.d
sudo chmod +x /etc/init.d/start_telegram_bot.sh
sudo update-rc.d /etc/init.d/start_telegram_bot.sh defaults

 echo "Completed successfullty."

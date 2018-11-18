#!/bin/bash
 
  echo "Install packages..."
  sudo apt-get update
  sudo apt-get install --assume-yes git git-lfs tmux software-properties-common apt-transport-https python3-pip
 
 echo "Install python dependencies..."
 sudo pip3 install -r requirements.txt
 
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

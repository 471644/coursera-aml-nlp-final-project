# coursera-aml-nlp-final-project
Stack Overflow assistant and chit-chat bot for Telegram 

# Deploying

Run following in your VM instance's terminal:

```
  sudo apt-get update

  sudo apt-get install software-properties-common curl
  sudo add-apt-repository ppa:git-core/ppa
  curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | sudo bash
  sudo apt-get install git git-lfs
  git lfs install

  sudo apt-get install tmux apt-transport-https python3-pip
  
  git clone https://github.com/vBLFTePebWNi6c/coursera-aml-nlp-final-project.git
  cd coursera-aml-nlp-final-project
  sh deploy.sh
```

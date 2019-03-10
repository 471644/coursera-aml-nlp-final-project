# Environment setup
FROM ubuntu:16.04
WORKDIR /usr/local/telegram_bot

ENV TELEGRAM_TOKEN 725572275:AAF86tc6KZDvj2fuzUguh5yGIqScuKAzIUI
ENV TELEGRAM_MASTER george_ignatov
ENV LC_ALL C.UTF-8
ENV LANG C.UTF-8

# Packages installation
RUN apt-get update \
&&  apt-get install -y \
    software-properties-common \
    curl \
    apt-transport-https \
    python3-pip

RUN add-apt-repository ppa:git-core/ppa \
&&  curl -s https://packagecloud.io/install/repositories/github/git-lfs/script.deb.sh | bash \
&&  apt-get install -y git git-lfs \
&&  git lfs install

RUN git clone https://github.com/vBLFTePebWNi6c/coursera-aml-nlp-final-project.git .

RUN pip3 install pipenv \
&&  pipenv install --system --ignore-pipfile --python $(python3 --version | grep -E -o '[0-9].[0-9](.[0-9])?')

# Working process
CMD ["python3", "main_bot.py"]
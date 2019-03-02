#!/usr/bin/env python3
# encoding=utf8

import warnings
warnings.filterwarnings("ignore")

import os
os.environ["OMP_NUM_THREADS"] = "1" # fix for greedy numpy behavior

import time
import json
import argparse

import requests
from requests.compat import urljoin

from dialogue_manager import DialogueManager
from utils import *

import logging

# set up logging to file - see previous section for more details
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename=os.path.abspath('./bot.log'),
                    filemode='w+')

console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s'))
logging.getLogger('').addHandler(console)

bot_logger = logging.getLogger('bot')
msg_logger = logging.getLogger('message')

class BotHandler(object):
    """
        BotHandler is a class which implements all back-end of the bot.
        It has tree main functions:
            'get_updates' — checks for new messages
            'send_message' – posts new message to user
            'get_answer' — computes the most relevant on a user's question
    """

    def __init__(self, token, dialogue_manager, proxies=None):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.dialogue_manager = dialogue_manager
        
        if proxies:
            self.proxies = proxies
        else:
            self.proxies = self.get_random_proxies()
            bot_logger.info("Proxy changed to {}.".format(self.proxies))
        
    def get_random_proxies(self):
        proxy_info = requests.get("https://api.getproxylist.com/proxy").json()
        proxy_string = "{protocol}://{ip}:{port}".format(**proxy_info)
        return {"https": proxy_string, "http": proxy_string}
        
    def get_updates(self, offset=None, timeout=30):
        params = {"timeout": timeout, "offset": offset}
        
        try:
            raw_resp = requests.get(urljoin(self.api_url, "getUpdates"), params, proxies=self.proxies)
        except requests.exceptions.ConnectionError as e:
            bot_logger.warning("Failed to get updates: {}.".format(e))
            self.proxies = self.get_random_proxies()
            bot_logger.info("Proxy changed to {}.".format(self.proxies))
            return []

        try:
            resp = raw_resp.json()
        except json.decoder.JSONDecodeError as e:
            bot_logger.warning("Failed to parse response {}: {}.".format(raw_resp.content, e))
            return []

        if "result" not in resp:
            return []
        return resp["result"]

    def send_message(self, chat_id, text):
        params = {"chat_id": chat_id, "text": text}
        return requests.post(urljoin(self.api_url, "sendMessage"), params, proxies=self.proxies)

    def get_answer(self, question):
        if question == '/start':
            return "Hello! I'm just like lowcost Jarvis, but even slightly worse :)\n Try to talk with me!"
        return self.dialogue_manager.generate_answer(question)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, default="")
    return parser.parse_args()

def is_unicode(text):
    return len(text) == len(text.encode())

def main():
    args = parse_args()
    token = args.token

    if not token:
        if not "TELEGRAM_TOKEN" in os.environ:
            print("Please, set bot token through --token or TELEGRAM_TOKEN env variable")
            return
        token = os.environ["TELEGRAM_TOKEN"]

    dialogue_manager = DialogueManager(RESOURCE_PATH)
    bot = BotHandler(token, dialogue_manager)

    bot_logger.info("Ready to talk!")
    offset = 0
    while True:
        updates = bot.get_updates(offset=offset)
        for update in updates:
            bot_logger.info("An update received.")
            if "message" in update:
                chat_id = update["message"]["chat"]["id"]
                if "text" in update["message"]:
                    bot_logger.info("Update content: {}".format(update))
                    username = update['message']['from']['username']
                    text = update["message"]["text"]
                    if is_unicode(text):
                        answer = bot.get_answer(update["message"]["text"])
                        bot.send_message(chat_id, bot.get_answer(update["message"]["text"]))
                        msg_logger.info("{}: '{}' --> {}".format(username, text, answer))
                    else:
                        bot.send_message(chat_id, "Hmm, you are sending some weird characters to me...")
            offset = max(offset, update["update_id"] + 1)
        time.sleep(1)
        
if __name__ == "__main__":
    main()

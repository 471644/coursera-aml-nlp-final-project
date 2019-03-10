#!/usr/bin/env python3
# encoding=utf8

import warnings
warnings.filterwarnings("ignore")

import tensorflow as tf
tf.logging.set_verbosity(tf.logging.ERROR)

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

class BotHandler(object):
    """
        BotHandler is a class which implements all back-end of the bot.
        It has tree main functions:
            'get_updates' — checks for new messages
            'send_message' – posts new message to user
            'get_answer' — computes the most relevant on a user's question
    """

    def __init__(self, token, dialogue_manager, master_name=None, 
                 proxies={"https": "socks5://userid04Iz:M3F4gsl@185.20.184.42:5928", "http": "socks5://userid04Iz:M3F4gsl@185.20.184.42:5928"}):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)
        self.dialogue_manager = dialogue_manager
        self.master_name = master_name
        self.dialogs = {}
        
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

    def get_answer(self, question, user_name=None):
        if question == '/start':
            return "Hello! I'm just like lowcost Jarvis, but even slightly worse :)\nTry to talk with me!"
        elif len(question) != len(question.encode()):
            return "Hmm, you are sending some weird characters to me..."
        elif question.startswith('/') and user_name == self.master_name:
            return self.serve_master_commands(question)
        else:
            answer = self.dialogue_manager.generate_answer(question)
            
            self.dialogs[user_name] = self.dialogs.get(user_name, [])
            self.dialogs[user_name] += ["{}: {}".format(user_name, question)]
            self.dialogs[user_name] += ["The Bot: {}".format(answer)]
                
            return answer
    
    def serve_master_commands(self, question):
        if question == '/report':
            return "I'm alive, Boss!\nI had handle {} new dialogs with other people.".format(len(self.dialogs))
        elif question == '/snitch':
            if len(self.dialogs):
                report = ""
                for user_name, history in self.dialogs.items():
                    report += "--- {} ---\n".format(user_name)
                    report += "\n".join(history)
                    report += "\n\n"
                    
                self.dialogs = {}
                return report
            else:
                return "There is nothing to read, Boss."
        else:
            return "Sorry, Boss! I don't understand :("

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", type=str, default="")
    parser.add_argument("--master", type=str, default=None)
    return parser.parse_args()

def main():
    args = parse_args()
    
    token = args.token
    if not token and "TELEGRAM_TOKEN" in os.environ:
        token = os.environ["TELEGRAM_TOKEN"]
        
    if not token:
        bot_logger.error("Please, set bot token through --token or TELEGRAM_TOKEN env variable")
        return
        
    master = args.master
    if not token and "TELEGRAM_MASTER" in os.environ:
        master = os.environ["TELEGRAM_MASTER"] 
        
    if not master:
        bot_logger.warning("The Bot hasn't master."
                           "To use master commands,"
                           "put your username through --master or TELEGRAM_MASTER env variable.")

    dialogue_manager = DialogueManager(RESOURCE_PATH)
    bot = BotHandler(token, dialogue_manager, master_name=master)

    bot_logger.info("Ready to talk!")
    offset = 0
    while True:
        time.sleep(1)
        updates = bot.get_updates(offset=offset)
        for update in updates:
            bot_logger.info("Update content: {}".format(update))
            offset = max(offset, update["update_id"] + 1)
            
            if update.get("message", {}).get("text", None):
                chat_id = update["message"]["chat"]["id"]
                user_name = update['message']['from']['username']
                text = update["message"]["text"]
                
                answer = bot.get_answer(text, user_name)
                bot_logger.info("Answer: {}".format(answer))
                bot.send_message(chat_id, answer)
        
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        bot_logger.error(str(e))
        raise

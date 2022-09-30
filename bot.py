import os
import json
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id


class Kitty_Bot:

    token = ""
    group_id = 0
    random_id = 200000
    longpoll = ""
    vk_session = ""

    def __init__(self):
        config_file = open('/Users/ash/Desktop/kittybot/config.json')
        data = json.load(config_file)
        self.token = data['vk_secret_token']
        self.group_id = data['vk_group_id']
        config_file.close()

        self.vk_session = vk_api.VkApi(token=self.token)
        self.longpoll = VkBotLongPoll(self.vk_session, self.group_id)
    
    def send_message(self, id, message):
        self.vk_session.method('messages.send', {'chat_id':id, 'message':message, 'random_id':self.random_id})


bot = Kitty_Bot()

for event in bot.longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_chat:

            id = event.chat_id
            msg = event.object.message['text'].lower()

            if len(msg) > 1:
                bot.send_message(id, "Кхе")
                bot.random_id += 1
import os
import json
import glob
import time
import vk_api
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


class Kitty_Bot:

    token = ""
    group_id = 0
    longpoll = ""
    vk_session = ""
    active_sess = ""
    cute_cats_url = ""
    lucky_times = []

    def __init__(self):
        config_file = open('/Users/ash/Desktop/kittybot/config.json')
        data = json.load(config_file)

        self.token = data['vk_secret_token']
        self.group_id = data['vk_group_id']
        self.cute_cats_url = data['ccurl']

        config_file.close()

        self.vk_session = vk_api.VkApi(token=self.token)
        self.longpoll = VkBotLongPoll(self.vk_session, self.group_id)
        self.active_sess = self.vk_session.get_api()
        # self.arrange_post_hours()

    def get_random_int(self) -> int:
        curr_dt = datetime.now()
        timestamp = int(round(curr_dt.timestamp()))
        return timestamp
    
    # def arrange_post_hours(self) -> list:
    #     self.lucky_times.clear()
    #     for _ in range(10):
    #         self.lucky_time.append([random.randint(11, 20), random.randint(0, 59)])
    #     self.lucky_times.sort()
    #     return self.lucky_time

    def send_message(self, id, message):
        self.vk_session.method('messages.send', {'chat_id':id, 'message':message, 'random_id':get_random_id()})
    
    def find_picture(self):
        old_files = glob.glob("/Users/ash/Desktop/kittybot/images/*")  # Clean directory for a new pic
        for file in old_files:
            os.remove(file)

        getURL = requests.get(self.cute_cats_url, headers={"User-Agent":"Mozilla/5.0"})  # Scrape url for pics
        soup = BeautifulSoup(getURL.text, 'html.parser')
        
        images = soup.find_all('img')
        resolvedURLs = []

        for image in images:
            src = image.get('src')
            resolvedURLs.append(requests.compat.urljoin(self.cute_cats_url, src))

        lucky_number = random.randint(0,len(resolvedURLs)-1)  # We need to post only one random cat

        webs = requests.get(resolvedURLs[lucky_number])
        open('images/' + "test.png", 'wb').write(webs.content)

    def send_picture(self, photo_address='/Users/ash/Desktop/kittybot/images/test.png'):
        # self.vk_session.method("messages.send", {'chat_id':id, "message": "Вот вам кощька:(пока только эта)", "attachment": "photo258009994_457267819", 'random_id':self.random_id})
        messages_upload_server = self.vk_session.method("photos.getMessagesUploadServer")
        photo_upload_data = requests.post(messages_upload_server['upload_url'], files={'photo': open(photo_address, 'rb')}).json()
        saved_photo = self.vk_session.method('photos.saveMessagesPhoto', {'photo': photo_upload_data['photo'], 'server': photo_upload_data['server'], 'hash': photo_upload_data['hash']})[0]
        attachment = "photo{}_{}".format(saved_photo["owner_id"], saved_photo["id"])
        self.vk_session.method("messages.send", {'chat_id':id, "message": "Ваша кощька:", "attachment": attachment, "random_id": get_random_id()})


bot = Kitty_Bot()

for event in bot.longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.from_chat:

            id = event.chat_id
            msg = event.object.message['text'].lower()

            if len(msg) > 1:
                bot.find_picture()
                bot.send_picture()  #TODO Add exception handler for files that are empty

    #TODO Add information displaying as well as greeting and goodbye messages
    # elif event.type == VkBotEventType.GROUP_JOIN:
    #     if event.from_chat:
    #         id = event.chat_id
    #         bot.send_message(id, "Я - Кошкобот\nПриносить кощек в чаты - моя задача\nЧтобы попросить у меня кощьку - просто напиши мне что-нибудь")
    #     print("lol")

    # elif event.type == VkBotEventType.GROUP_LEAVE:
    #         bot.send_message()
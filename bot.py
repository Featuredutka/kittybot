import os
import json
import glob
import time
import vk_api
import random
import requests
import psycopg2
import multiprocessing as mps
import origtest as orig
from bs4 import BeautifulSoup
from datetime import datetime
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

IMAGE_PATH = "./images/test.png"
# IMAGE_PATH = "/Users/ash/Desktop/test.png"  # DEBUGGING EMPTY PICTURE

def reconnect():
    CONNECTION = psycopg2.connect(user="newuser",
                                    password="password",
                                    host="localhost",
                                    port="5432",
                                    database="hashes")
    return CONNECTION


class Kitty_Bot:

    token = ""
    group_id = 2
    longpoll = ""
    vk_session = ""
    active_sess = ""
    cute_cats_url = []

    manual_responses = []
    auto_responses = []

    def __init__(self):
        config_file = open('config.json')  # Loading configurations for VK Auth
        data = json.load(config_file)

        self.token = data['vk_secret_token']
        self.group_id = data['vk_group_id']
        self.cute_cats_url = data['ccurl']

        config_file.close()

        self.vk_session = vk_api.VkApi(token=self.token)
        self.longpoll = VkBotLongPoll(self.vk_session, self.group_id)
        self.active_sess = self.vk_session.get_api()

        dictionary = open('dictionary.json')    # Loading response phrases
        data = json.load(dictionary)

        self.manual_responses = data['manual_responses']
        self.auto_responses = data['auto_responses']

        dictionary.close()

        print("Bot is ACTIVE --- ", end="")

    def __del__(self):
        print("Bot is STOPPED")

    def get_random_int(self) -> int:    # Getting a random int for message unique id (required by Vk send_message)
        curr_dt = datetime.now()
        timestamp = int(round(curr_dt.timestamp()))
        return timestamp

    def send_message(self, id, message):
        self.vk_session.method('messages.send', {'chat_id':id, 'message':message, 'random_id':get_random_id()})

    def find_picture(self):
        old_files = glob.glob("./images/*")  # Clean directory for a new pic
        for file in old_files:
            os.remove(file)

        current_source = self.cute_cats_url[random.randint(0, len(self.cute_cats_url)-1)]
        getURL = requests.get(current_source, headers={"User-Agent":"Mozilla/5.0"})  # Scrape url for pics
        soup = BeautifulSoup(getURL.text, 'html.parser')

        images = soup.find_all('img')
        resolvedURLs = []

        for image in images:
            src = image.get('src')
            resolvedURLs.append(requests.compat.urljoin(current_source, src))

        lucky_number = random.randint(0,len(resolvedURLs)-1)  # We need to post only one random cat

        webs = requests.get(resolvedURLs[lucky_number])
        with open('images/' + "test.png", 'wb') as im:
            im.write(webs.content)
            im.close()


    def send_picture(self, id, response, photo_address=IMAGE_PATH):
        # self.vk_session.method("messages.send", {'chat_id':id, "message": "Вот вам кощька:(пока только эта)", "attachment": "photo258009994_457267819", 'random_id':self.random_id})
        messages_upload_server = self.vk_session.method("photos.getMessagesUploadServer")
        photo_upload_data = requests.post(messages_upload_server['upload_url'], files={'photo': open(photo_address, 'rb')}).json()
        saved_photo = self.vk_session.method('photos.saveMessagesPhoto', {'photo': photo_upload_data['photo'], 'server': photo_upload_data['server'], 'hash': photo_upload_data['hash']})[0]
        attachment = "photo{}_{}".format(saved_photo["owner_id"], saved_photo["id"])
        self.vk_session.method("messages.send", {'chat_id':id, "message": response[random.randint(0, len(response)-1)], "attachment": attachment, "random_id": get_random_id()})

def main_bot_loop():
    try:
        try:
            cursor = CONNECTION.cursor()  # Connecting to the database
        except:
            CONNECTION = reconnect()
            cursor = CONNECTION.cursor()
        bot = Kitty_Bot()
        print(main_bot_loop.__name__)

        for event in bot.longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                if event.from_chat:

                    id = event.chat_id
                    msg = event.object.message['text'].lower()

                    if len(msg) > 1:  #Manual response handling
                        bot.find_picture()
                        while os.stat(IMAGE_PATH).st_size < 1000:  # Preventing empty images from being sent (empty size usually is 919 bytes but further research is needed)
                            bot.find_picture()
                        while orig.search_for_duplicate(orig.get_image_hash(IMAGE_PATH), cursor) == None: # Preventing duplicate images from being sent
                            bot.find_picture()
                        bot.send_picture(id, bot.manual_responses)
                        CONNECTION.commit()

    except KeyboardInterrupt:
        print("\nYou interrupted the work manually")

def get_time() -> list:
    lucky_times = []
    for _ in range(10):
        lucky_times.append([random.randint(11, 20), random.randint(0, 59)])
    lucky_times.sort()
    print("Posting time - ", end=" ")
    for _ in lucky_times:
        print(str(_[0]) + ":" + str(_[1]), end=" ")
    print("")
    return lucky_times

def autonomous_bot_loop():
    times = get_time()
    bot = Kitty_Bot()
    print(autonomous_bot_loop.__name__)
    while True:
        currentDateAndTime = datetime.now()
        currentTime = [currentDateAndTime.hour, currentDateAndTime.minute]
        for thing in times:
            if currentTime[0] == thing[0] and currentTime[1] == thing[1]:
                id = 2  # TODO For every chat - do a post based on the id (or just tie it to one single chat which is a shitty idea)
                try:
                    cursor = CONNECTION.cursor()  # Connecting to the database
                except:
                    CONNECTION = reconnect()
                    cursor = CONNECTION.cursor()
                bot.find_picture()
                while os.stat(IMAGE_PATH).st_size < 1000:  # Preventing empty images from being sent (empty size usually is 919 bytes but further research is needed)
                    bot.find_picture()
                while orig.search_for_duplicate(orig.get_image_hash(IMAGE_PATH), cursor) == None: # Preventing duplicate images from being sent
                    bot.find_picture()
                bot.send_picture(id, bot.auto_responses)
                CONNECTION.commit()
                times.pop(0)  # Delete the first element from array (pop da stack) TODO - maybe use a stack instead of the list
        if currentTime[0] == 9 and currentTime[1] == 0:
            times = get_time()
        time.sleep(60)


if __name__ == "__main__":
    CONNECTION = reconnect()

    proc_list = []
    request_loop = mps.Process(target=main_bot_loop)
    auto_loop = mps.Process(target=autonomous_bot_loop)
    proc_list.append(request_loop)
    proc_list.append(auto_loop)
    request_loop.start()
    auto_loop.start()
    request_loop.join()
    auto_loop.join()
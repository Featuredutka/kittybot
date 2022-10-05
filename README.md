# kittybot
A simple bot for sending cat pictures to work chats made with VK API

<aside>
💡 **v.1.0**

</aside>

- [x]  Parse web for cats
- [x]  Send cats
- [x]  Send messages to chats with VK API
- [x]  Random ints generation tied to timeline for unique message ids

<aside>
💡 **v.1.1**

</aside>

- [ ]  Greetings and farewells
- [ ]  Exceptions for empty files
- [ ]  Check repeating images (hash?) and send only new ones **(MD5?)**
- [ ]  **README with instructions**
- [ ]  Get acquainted with the VK pipeline and comment it in code
- [ ]  Transfer project to Raspberry server and let it work in a loop
- [ ]  Different replies (dictionary)
- [ ]  Different animals
- [ ]  **Automatic posting (time-tied) - checking current time**
    - [ ]  Two async loops
        - [ ]  1 - longpoll listener
        - [ ]  2 - time check procedure for posting within active time periods

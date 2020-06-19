import os
import validators
import telebot
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

import config


bot = telebot.TeleBot(config.token, threaded=False)


@bot.message_handler(commands=['start'])
def hello_user(message):
    bot.send_message(message.chat.id,
                     f"Hello, {message.from_user.username}!"
                     + "\nGive me a link and I will return the SCREEN to you;)")
    
    
@bot.message_handler(content_types=['text'])
def get_screenshot(message):
    uid = message.chat.id
    url = message.text

    if validators.url(url):
        photo_path = str(uid) + '.png'
        driver = webdriver.Chrome(ChromeDriverManager().install())
        driver.maximize_window()
        driver.get(url)
        element = driver.find_element_by_tag_name('body')
        element.screenshot(photo_path)
        bot.send_photo(uid, photo = open(photo_path, 'rb'))
        driver.quit()
        os.remove(photo_path)
    else:
        bot.send_message(uid, 'URL is invalid!')
        

if __name__ == '__main__':
    bot.infinity_polling()

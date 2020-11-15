import os
import validators
import telebot
from selenium import webdriver
from flask import Flask, request


TOKEN = os.environ.get("TOKEN")
URL = os.environ.get("URL")

bot = telebot.TeleBot(TOKEN, threaded=False)
app = Flask(__name__)


@app.route('/' + TOKEN, methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return 'ok', 200


@app.route('/')
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=URL + TOKEN)
    return 'ok', 200


@bot.message_handler(commands=['start', 'help'])
def hello_user(message):
    bot.send_message(message.chat.id,
                     f"Hello, {message.from_user.username}!"
                     + "\nGive me a link and I will return the SCREENSHOT to you;)")


@bot.message_handler(content_types=['text'])
def get_screenshot(message):
    uid = message.chat.id
    url = message.text

    if validators.url(url):
        bot.send_message(uid, 'Wait a minute, please!)')
        
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')      
        chrome_options.add_argument("--start-maximized")
        chrome_options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
        
        browser = webdriver.Chrome(os.environ.get("CHROMEDRIVER_PATH"), chrome_options=chrome_options)
        
        try:
            browser.get(url)

            required_width = browser.execute_script('return document.body.parentNode.scrollWidth')
            required_height = browser.execute_script('return document.body.parentNode.scrollHeight')
            browser.set_window_size(required_width, required_height)
            browser.find_element_by_tag_name('body').screenshot("simple.png")
 
            bot.send_document(uid, open("simple.png", 'rb'))
            
        finally:
            browser.quit()
            os.remove("simple.png")
            bot.send_message(uid, 'Thanks for using! ^^,)')

    else:
        bot.send_message(uid, 'URL is invalid!')

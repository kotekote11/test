import json
import logging
import os
import time
from datetime import datetime
from os import getenv
from requests.exceptions import ConnectionError
from telegram import Bot
from telegram import InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CallbackQueryHandler, InlineQueryHandler, Updater

logging.basicConfig(filename='main.log', level=logging.DEBUG)

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_LIST_FILE = 'google.json'

KEYWORDS = "открытие фонтанов"
IGNORE_SITES = ["instagram", "livejournal", "fontanka"]
IGNORE_WORDS = ["нефть", "недр", "месторождение"]

bot = Bot(token=API_TOKEN)

def query(url: str):
    try:
        response = requests.head(url, allow_redirects=True)
        if response.status_code == 200:
            return response.url
        else:
            return None
    except ConnectionError:
        return None

def clean_url(url: str):
    url = url[len('/url?q='):]
    url = url.split('&sa=U&ved')[0]
    return url

def send_message(title: str, link: str):
    if any(word in link for word in IGNORE_WORDS):
        return
    cleaned_link = clean_url(link)
    if any(site in cleaned_link for site in IGNORE_SITES):
        return
    if requests.head(cleaned_link).status_code == 200:
        with open(SENT_LIST_FILE) as file:
            sent_list = json.load(file)
        if cleaned_link not in sent_list:
            message_text = f"{title}\n{link}\n⛲@MonitoringFontan📰#MonitoringFontan"
            bot.send_message(chat_id=CHANNEL_ID, text=message_text)
            sent_list.append(cleaned_link)
            save_sent_list(sent_list)

def save_sent_list(sent_list):
    with open(SENT_LIST_FILE, 'w') as file:
        json.dump(sent_list, file, indent=2, ensure_ascii=False)

def inlinequery(update, context):
    query = update.inline_query.query
    if not query:
        return
    if KEYWORDS in query.lower():
        with open(SENT_LIST_FILE) as file:
            sent_list = json.load(file)
        results = []
        for url in sent_list:
            title = url.split('/')[-1].replace('.html', '').replace('-', ' ').title()
            results.append(
                InlineQueryResultArticle(
                    id=url,
                    title=title,
                    input_message_content=InputTextMessageContent(message_text=f"{title}\n{url}")
                )
            )
        update.inline_query.answer(results)

def callbackquery(update, context):
    query = update.callback_query
    if query.data == 'get_new':
        check_new_posts()

def check_new_posts():
    repeat_count = 0
    while True:
        try:
            google_query = f'https://www.google.ru/search?q={KEYWORDS}&hl=ru&tbs=qdr:d'
            response = requests.get(google_query)
            soup = BeautifulSoup(response.text, 'html.parser')
            posts = soup.find_all('h3')
            for post in posts:
                link = post.find('a').get('href')
                title = post.text
                send_message(title, link)
            time.sleep(300)
            repeat_count += 1
            if repeat_count % 90 == 0:
                with open(SENT_LIST_FILE) as file:
                    sent_list = json.load(file)
                sent_list = sent_list[-9:]
                save_sent_list(sent_list)
        except Exception as e:
            logging.error(e)
            time.sleep(300)

if __name__ == '__main__':
    updater = Updater(API_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CallbackQueryHandler(callbackquery))
    dispatcher.add_handler(InlineQueryHandler(inlinequery))

    updater.start_webhook(listen="0.0.0.0", port=int(getenv("PORT", 5000)), url_path=API_TOKEN)
    updater.idle()

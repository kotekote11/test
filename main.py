import requests

from bs4 import BeautifulSoup

import json

import logging

import time
import os

YOUR_BOT_TOKEN = os.getenv("API_TOKEN")

YOUR_CHAT_ID = os.getenv("CHANNEL_ID")
# Настройка логирования

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Загрузка уже отправленных новостей

try:

    with open('sent_news.json', 'r') as file:

        sent_news = json.load(file)

except FileNotFoundError:

    sent_news = []

# Поиск новостей по ключевым словам

keywords = "новости доллар"

url = "https://www.google.ru/search?q=" + keywords

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

# Парсинг новостей

news = [{'title': item.text, 'link': item['href']} for item in soup.find_all('a', href=True) if 'http' in item['href']]

new_news = [item for item in news if item['link'] not in sent_news]

# Отправка новых новостей в Telegram

if new_news:

    for item in new_news:

        requests.get(f"https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage?chat_id=<YOUR_CHAT_ID>&text={item['title']} {item['link']}")

        sent_news.append(item['link'])

    with open('sent_news.json', 'w') as file:

        json.dump(sent_news, file)

# Пауза перед следующим запросом

time.sleep(200)


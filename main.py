import requests

from bs4 import BeautifulSoup

import logging

import time

import os

TELEGRAM_TOKEN = os.getenv("API_TOKEN")

CHAT_ID = os.getenv("CHANNEL_ID")

# Настройка логирования

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



# URL для проверки новостей в Telegram

TELEGRAM_CHANNEL_URL = 'https://t.me/s/fgtestfg'

# Ключевые слова для поиска

KEYWORDS = "фонтан музыкальный открытие"

def clean_url(url):

   """Очищает URL, оставляя только нужный адрес."""

   url = url[len('/url?q='):]  # Убираем префикс

   return url.split('&sa=U&ved')[0]  # Убираем лишние параметры

def fetch_telegram_links():

   """Получает ссылки на новости из Telegram-канала."""

   response = requests.get(TELEGRAM_CHANNEL_URL)

   soup = BeautifulSoup(response.text, 'html.parser')

   links = set()

   for link in soup.find_all('a', class_='tgme_widget_message_link_preview'):

       href = link['href']

       links.add(href)

   

   return links  # Возвращаем уникальные ссылки

def is_link_working(link):

   """Проверяет доступность ссылки."""

   try:

       response = requests.get(link, timeout=5)

       return response.status_code == 200

   except requests.RequestException as e:

       logging.warning(f'Проблема с доступом к ссылке: {link} - {e}')

       return False

def send_telegram_message(message):

   """Отправляет сообщение в Telegram."""

   url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

   data = {

       'chat_id': CHAT_ID,

       'text': message,

       'parse_mode': 'HTML'

   }

   response = requests.post(url, data=data)

   return response.json()

def search_news():

   """Ищет новости по ключевым словам на Google."""

   query = f'https://www.google.ru/search?q={KEYWORDS}&hl=ru'

   response = requests.get(query)

   soup = BeautifulSoup(response.text, 'html.parser')

   news_items = []

   for item in soup.find_all('h3'):

       link = item.find_parent('a')  # Получаем родительский элемент <a>

       if link:

           clean_link = clean_url(link['href'])

           title = item.get_text(strip=True)

           news_items.append({'title': title, 'link': clean_link})

   return news_items

def main():

   """Основная логика."""

   known_links = fetch_telegram_links()  # Получаем известные ссылки из Telegram

   

   news_items = search_news()

   logging.info(f'Найдено {len(news_items)} новостей.')

   for news in news_items:

       if news['link'] not in known_links and is_link_working(news['link']):  # Если ссылка новая и рабочая

           message = f'<b>{news["title"]}</b>\n{news["link"]}'

           response = send_telegram_message(message)

           if response.get('ok'):

               logging.info(f'Отправлено: {news["title"]}')

           else:

               logging.error(f'Ошибка отправки: {response}')

       elif news['link'] in known_links:

           logging.info(f'Новость уже существует в Telegram: {news["title"]}')

       else:

           logging.info(f'Ссылка не рабочая: {news["link"]}')

if __name__ == "__main__":

   while True:

       main()

       time.sleep(200)  # Подождите 200 секунд перед следующим запросом

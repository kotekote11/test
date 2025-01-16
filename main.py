import os
import json
import logging
import asyncio
import random
import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup

# Задаем переменные окружения для токенов и других настроек
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_LIST_FILE = 'dump.json'

KEYWORDS = [
    "открытие фонтанов 2025",
    "открытие фонтанов 2026",
    "открытие светомузыкального фонтана 2025",
]

IGNORE_WORDS = {"Петергоф", "нефть", "недр", "месторождение"}
IGNORE_SITES = {"instagram", "livejournal", "fontanka"}

logging.basicConfig(level=logging.DEBUG)

# Загрузка ранее отправленных сообщений
def load_sent_list():
    if os.path.exists(SENT_LIST_FILE):
        with open(SENT_LIST_FILE, 'r') as file:
            return json.load(file)
    return []

# Сохранение отправленных сообщений
def save_sent_list(sent_list):
    with open(SENT_LIST_FILE, 'w') as file:
        json.dump(sent_list, file)

# Очистка URL
def clean_url(url):
    url = url[len('/url?q='):]
    url = url.split('&sa=U&ved')[0]
    return url

# Отправка сообщения в Telegram
async def send_message(session, message_text):
    url = f'https://api.telegram.org/bot{API_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHANNEL_ID,
        'text': message_text,
        'parse_mode': 'Markdown'
    }
    async with session.post(url, json=payload) as response:
        if response.status == 200:
            logging.info('Сообщение успешно отправлено.')
        else:
            logging.error('Ошибка отправки сообщения.')

# Поиск новостей в Google
async def search_google(session, keyword):
    query = f'https://www.google.ru/search?q={keyword}&hl=ru&tbs=qdr:d'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    async with session.get(query, headers=headers) as response:
        if response.status != 200:
            logging.error(f'Ошибка при обращении к Google: {response.status}')
            return []
        soup = BeautifulSoup(await response.text(), 'html.parser')
        return [(item.get_text(), clean_url(item.find_parent('a')['href']))
                for item in soup.find_all('h3') if item.find_parent('a')]

# Поиск новостей в Yandex
async def search_yandex(session, keyword):
    query = f'https://yandex.ru/search/?text={keyword}&within=77'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'
    }
    async with session.get(query, headers=headers) as response:
        if response.status != 200:
            logging.error(f'Ошибка при обращении к Yandex: {response.status}')
            return []
        soup = BeautifulSoup(await response.text(), 'html.parser')
        results = []
        
        for item in soup.find_all('h2'):
            parent_link = item.find_parent('a')
            if parent_link and 'href' in parent_link.attrs:
                link = clean_url(parent_link['href'])
                results.append((item.get_text(), link))
        
        return results

# Проверка новостей
async def check_news(sem, sent_list):
    async with ClientSession() as session:
        for keyword in KEYWORDS:
            async with sem:
                logging.info(f'Проверка новостей для: {keyword}')

                news_from_google = await search_google(session, keyword)
                news_from_yandex = await search_yandex(session, keyword)
                
                all_news = news_from_google + news_from_yandex

                for title, link in all_news:
                    if any(ignore in title for ignore in IGNORE_WORDS) or any(ignore in link for ignore in IGNORE_SITES):
                        continue

                    if link not in sent_list:
                        sent_list.append(link)
                        message_text = f"{title}\n{link}\n⛲@MonitoringFontan📰#Фонтан"
                        await send_message(session, message_text)

                        # Сохраняем отправленные ссылки каждые 90 сообщений
                        if len(sent_list) % 90 == 0:
                            save_sent_list(sent_list)

                # Случайная пауза между запросами
                await asyncio.sleep(random.randint(5, 15))

async def main():
    sem = asyncio.Semaphore(5)  # Ограничение на количество параллельных запросов
    sent_list = load_sent_list()

    while True:
        await check_news(sem, sent_list)
        save_sent_list(sent_list)
        await asyncio.sleep(300)  # Проверка каждые 5 минут

if __name__ == '__main__':
    asyncio.run(main())

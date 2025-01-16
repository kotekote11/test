import os
import json
import random
import logging
import aiohttp
import asyncio
from aiogram import Bot
from aiogram.utils import executor
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
# Ключевые слова для поиска
KEYWORDS = [
    "открытие фонтанов 2025",
    "открытие фонтанов 2026",
    "открытие светомузыкального фонтана 2025"
]
IGNORE_WORDS = {"Петергоф", "нефть", "недр", "месторождение"}
IGNORE_SITES = {"instagram", "livejournal", "fontanka"}
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]
# Файл для хранения отправленных постов
SENT_LIST_FILE = 'dum1p.json'
bot = Bot(token=API_TOKEN)
# Функция для загрузки ранее отправленных ссылок
def load_sent_list():
    if os.path.exists(SENT_LIST_FILE):
        with open(SENT_LIST_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []
# Функция для очистки URL от лишних частей
def clean_url_google(url):
    url = url[len('/url?q='):]
    return url.split('&sa=U&ved')[0]
def clean_url_yandex(url):
    url = url[len('::::'):]
    return url.split('&&&&&')[0]
# Поиск новостей в Google
async def search_google(session, keyword):
    search_url = f'https://www.google.ru/search?q={keyword}&hl=ru&tbs=qdr:d'
    headers = {'User-Agent': random.choice(user_agents)}
    async with session.get(search_url, headers=headers) as response:
        if response.status != 200:
            logging.error(f'Ошибка при обращении к Google: {response.status}')
            return []
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        for item in soup.find_all('h3'):
            link = item.find_parent('a')['href']
            cleaned_link = clean_url_google(link)
            articles.append((item.get_text(), cleaned_link))
        return articles
# Поиск новостей в Яндексе
async def search_yandex(session, keyword):
    search_url = f'https://yandex.ru/search/?text={keyword}&within=77'
    headers = {'User-Agent': random.choice(user_agents)}
    async with session.get(search_url, headers=headers) as response:
        if response.status != 200:
            logging.error(f'Ошибка при обращении к Яндексу: {response.status}')
            return []
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        for item in soup.find_all('h3'):
            link = item.find_parent('a')['href']
            cleaned_link = clean_url_yandex(link)
            articles.append((item.get_text(), cleaned_link))
        return articles
# Основная логика отправки сообщений
async def main():
    sent_set = set(load_sent_list())
    async with aiohttp.ClientSession() as session:
        for keyword in KEYWORDS:
            news_from_google = await search_google(session, keyword)
            news_from_yandex = await search_yandex(session, keyword)
            for title, link in news_from_google:
                if link not in sent_set:
                    message_text_google = f"{title}\n{link}\n⛲@MonitoringFontan📰#google"
                    await bot.send_message(CHANNEL_ID, message_text_google)
                    sent_set.add(link)
            for title, link in news_from_yandex:
                if link not in sent_set:
                    message_text_yandex = f"{title}\n{link}\n⛲@MonitoringFontan📰#yandex"
                    await bot.send_message(CHANNEL_ID, message_text_yandex)
                    sent_set.add(link)
            await asyncio.sleep(random.randint(5, 15))  # Пауза между запросами

if __name__ == '__main__':
    asyncio.run(main())

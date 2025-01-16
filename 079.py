import os
import json
import logging
import asyncio
import random
from aiohttp import ClientSession
from bs4 import BeautifulSoup

# Настройки Telegram API
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_LIST_FILE = 'dump.json'

# Ключевые слова для поиска
KEYWORDS = [
    "открытие фонтанов 2025",
    "открытие фонтанов 2026",
    "открытие светомузыкального фонтана 2025",
]

# Игнорируемые слова и сайты
IGNORE_WORDS = {"Петергоф", "нефть", "недр", "месторождение"}
IGNORE_SITES = {"instagram", "livejournal", "fontanka"}

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

# Функция для загрузки ранее отправленных сообщений из файла
def load_sent_list():
    if os.path.exists(SENT_LIST_FILE):
        with open(SENT_LIST_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

# Функция для сохранения отправленных сообщений в файл
def save_sent_list(sent_list):
    with open(SENT_LIST_FILE, 'w', encoding='utf-8') as file:
        json.dump(sent_list, file)

# Функция для очистки URL от лишних параметров
def clean_url(url):
    url = url[len('/url?q='):]
    url = url.split('&sa=U&ved')[0]
    return url

# Функция для отправки сообщения в Telegram
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
            logging.error(f'Ошибка отправки сообщения: {response.status}')

# Список User-Agent для случайного выбора
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
]

# Функция для поиска новостей в Google
async def search_google(session, keyword):
    query = f'https://www.google.ru/search?q={keyword}&hl=ru&tbs=qdr:d'
    headers = {
        'User-Agent': random.choice(user_agents)
    }
    async with session.get(query, headers=headers) as response:
        if response.status != 200:
            logging.error(f'Ошибка при обращении к Google: {response.status}')
            return []
        
        soup = BeautifulSoup(await response.text(), 'html.parser')
        results = []
        
        # Найти все заголовки новостей
        for item in soup.find_all('h3'):
            parent_link = item.find_parent('a')
            if parent_link and 'href' in parent_link.attrs:

                link = clean_url(parent_link['href'])
                results.append((item.get_text(), link))
        
        return results

# Функция для поиска новостей в Yandex
async def search_yandex(session, keyword):
    query = f'https://yandex.ru/search/?text={keyword}&within=77'
    headers = {
        'User-Agent': random.choice(user_agents)
    }
    async with session.get(query, headers=headers) as response:
        if response.status != 200:
            logging.error(f'Ошибка при обращении к Yandex: {response.status}')
            return []
        
        soup = BeautifulSoup(await response.text(), 'html.parser')
        results = []
        
        # Найти все заголовки новостей
        for item in soup.find_all('h2'):
            parent_link = item.find_parent('a')
            if parent_link and 'href' in parent_link.attrs:
                link = clean_url(parent_link['href'])
                results.append((item.get_text(), link))
        
        return results

# Функция для проверки новостей по ключевым словам
async def check_news(sem, sent_list):
    async with ClientSession() as session:
        for keyword in KEYWORDS:
            async with sem:
                logging.info(f'Проверка новостей для: {keyword}')
                
                # Получаем новости из Google и Yandex
                news_from_google = await search_google(session, keyword)
                news_from_yandex = await search_yandex(session, keyword)
                
                all_news = news_from_google + news_from_yandex

                for title, link in all_news:
                    # Игнорируем слова и сайты из списка IGNORE_WORDS и IGNORE_SITES
                    if any(ignore in title for ignore in IGNORE_WORDS) or any(ignore in link for ignore in IGNORE_SITES):
                        continue
                    
                    # Проверяем, были ли ссылки отправлены ранее
                    if link not in sent_list:
                        sent_list.append(link)  # Добавляем новую ссылку в список
                        message_text = f"{title}\n{link}\n⛲@MonitoringFontan📰#Фонтан"
                        await send_message(session, message_text)  # Отправляем сообщение в Telegram
                        
                # Сохраняем отправленные ссылки после каждой проверки
                save_sent_list(sent_list)

                # Случайная пауза между запросами
                await asyncio.sleep(random.randint(5, 15))

# Основная функция
async def main():
    sem = asyncio.Semaphore(5)  # Ограничение на количество параллельных запросов
    sent_list = load_sent_list()  # Загружаем уже отправленные ссылки

    while True:
        await check_news(sem, sent_list)  # Проверка новостей
        await asyncio.sleep(300)  # Проверка каждые 5 минут

if __name__ == '__main__':
    asyncio.run(main())  # Запускаем основную функцию

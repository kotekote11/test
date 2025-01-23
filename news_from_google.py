import os
import json
import logging
import asyncio
import random
import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from urllib.parse import quote

# Настройки логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Настройки API Telegram
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_LIST_FILE = 'dump.json'

# Ключевые слова для поиска
KEYWORDS = [
    "открытие фонтана 2025",
    "открытие фонтана 2026",
    "строительство фонтана 2025",
]

# Обязательные и игнорируемые слова
MUST_HAVE_WORDS = {"фонтан", "светомузыкальн", "фонтана"}
IGNORE_WORDS = {"канализ", "нефть", "Объявления"}
IGNORE_SITES = {"instagram", "livejournal", "avito"}

# Функция для загрузки ранее отправленных ссылок
def load_sent_list():
    if os.path.exists(SENT_LIST_FILE):
        with open(SENT_LIST_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return []

# Функция для сохранения отправленных ссылок
def save_sent_list(sent_list):
    with open(SENT_LIST_FILE, 'w', encoding='utf-8') as file:
        json.dump(sent_list, file)

# Функция для отправки сообщения в Telegram
async def send_message(session, message):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHANNEL_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    async with session.post(url, json=payload) as response:
        if response.status != 200:
            logging.error(f'Ошибка отправки сообщения #fontan: {response.status} - {await response.text()}')

# Функция для проверки доступности ссылки
async def check_link_availability(link):
    try:
        response = requests.head(link)
        return response.status_code == 200
    except Exception as e:
        logging.warning(f'Проблема с доступом к ссылке #fontan: {link} - {e}')
        return False

# Функция для очистки URL
def clean_url(url):
    return url.split('?')[0]

# Функция для выполнения поиска на Yandex
async def search_yandex(session, keyword):
    encoded_keyword = quote(keyword)
    query = f'https://yandex.ru/search/?text={encoded_keyword}&within=77'
    user_agents = [
        "Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Mozilla/5.0 (Android 12; Mobile; rv:109.0) Gecko/113.0 Firefox/113.0",
    ]
    
    headers = {'User-Agent': random.choice(user_agents)}
    logging.debug(f'Запрашиваем Yandex по адресу: {query} с заголовками: {headers}')
    
    async with session.get(query, headers=headers) as response:
        if response.status != 200:
            logging.error(f'Ошибка при обращении к #fontan: {response.status} для запроса: {query}')
            return []
        
        soup = BeautifulSoup(await response.text(), 'html.parser')
        results = []

        for item in soup.find_all('h2'):
            parent_link = item.find_parent('a')
            if parent_link and 'href' in parent_link.attrs:
                link = clean_url(parent_link['href'])
                title = item.get_text()

                results.append((title, link))
        
        logging.info(f'Найдено {len(results)} результатов для {keyword} в #fontan.')
        return results

# Основная функция для проверки новостей
async def check_news(sem, sent_set):
    async with ClientSession() as session:
        for keyword in random.sample(KEYWORDS, len(KEYWORDS)):  # Перемешиваем KEYWORDS для случайного порядка
            async with sem:
                logging.info(f'Проверка новостей для: {keyword}')
                
                news_from_yandex = await search_yandex(session, keyword)

                for title, link in news_from_yandex:
                    if any(ignore in title for ignore in IGNORE_WORDS):
                        logging.info(f'Игнорируем заголовок: "{title}", так как он содержит игнорируемые слова.')
                        continue
                    
                    if any(ignore in link for ignore in IGNORE_SITES):
                        logging.info(f'Игнорируем ссылку: {link}, так как она содержит игнорируемые сайты.')
                        continue

                    if link not in sent_set and await check_link_availability(link):
                        sent_set.add(link)
                        message_text_yandex = f"{title}\n{link}\n⛲@MonitoringFontan📰#fontan"
                        await send_message(session, message_text_yandex)
                    else:
                        logging.info(f'Ссылка не рабочая #fontan: {link}')

                save_sent_list(list(sent_set))
                await asyncio.sleep(random.randint(5, 15))  # Пауза между обработкой результатов

# Основная функция
async def main():
    sem = asyncio.Semaphore(5)  # Ограничение на количество параллельных запросов
    sent_set = set(load_sent_list())  # Загружаем уже отправленные ссылки

    while True:
        await check_news(sem, sent_set)  # Проверка новостей
        await asyncio.sleep(1300)  # Пауза между проверками

if __name__ == '__main__':
    asyncio.run(main())  # Запускаем основную функцию

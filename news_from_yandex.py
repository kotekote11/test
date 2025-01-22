import os
import json
import logging
import asyncio
import random
import requests
from aiohttp import ClientSession
from bs4 import BeautifulSoup

# Уровень логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Настройки API Telegram
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_LIST_FILE = 'dump.json'

# Ключевые слова для поиска
KEYWORDS = [
    "открытие фонтанов 2025",
    "открытие фонтанов 2026",
    "открытие светомузыкального фонтана 2025",
]

# Обязательные и игнорируемые слова
MUST_HAVE_WORDS = {"фонтан", "фонтанов", "фонтана"}
IGNORE_WORDS = {"Петергоф", "нефть", "недр", "месторождение"}
IGNORE_SITES = {"instagram", "livejournal", "fontanka", "avito"}

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
        'parse_mode': 'Markdown'  # Форматирование текста
    }
    async with session.post(url, json=payload) as response:
        if response.status == 200:
            logging.info('Сообщение успешно отправлено.')
        else:
            logging.error(f'Ошибка отправки сообщения: {response.status} - {await response.text()}')

# Функция для очистки URL
def clean_url_yandex(url):
    return url.split('?')[0]

# Функция для проверки наличия обязательных слов
def contains_must_have_words(title):
    return any(word in title.lower() for word in MUST_HAVE_WORDS)

# Функция для поиска новостей в Yandex
async def search_yandex(session, keyword):
    query = f'https://yandex.ru/search/?text={keyword}&within=77'
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15'
    ]
    headers = {'User-Agent': random.choice(user_agents)}
    logging.debug(f'Запрашиваем Yandex по адресу: {query} с заголовками: {headers}')
    async with session.get(query, headers=headers) as response:
        if response.status != 200:
            logging.error(f'Ошибка при обращении к Yandex: {response.status} для запроса: {query}')
            return []
        logging.debug(f'Получен ответ от Yandex: {response.status}')
        soup = BeautifulSoup(await response.text(), 'html.parser')
        results = []

        for item in soup.find_all('h2'):
            parent_link = item.find_parent('a')
            if parent_link and 'href' in parent_link.attrs:

                link = clean_url_yandex(parent_link['href'])
                title = item.get_text()
                logging.debug(f'Найден заголовок: {title} с ссылкой: {link}')
                if contains_must_have_words(title):
                    results.append((title, link))
        logging.info(f'Найдено {len(results)} результатов для {keyword} в Yandex.')
        return results

# Основная функция для проверки новостей
async def check_news(sem, sent_set):
    async with ClientSession() as session:
        for keyword in KEYWORDS:
            async with sem:
                logging.info(f'Проверка новостей для: {keyword}')
                # Получаем новости из Yandex
                news_from_yandex = await search_yandex(session, keyword)

                for title, link in news_from_yandex:
                    if any(ignore in title for ignore in IGNORE_WORDS) or any(ignore in link for ignore in IGNORE_SITES):
                        continue
                    if link not in sent_set:
                        sent_set.add(link)
                        message_text = f"{title}\n{link}\n⛲@MonitoringFontan📰#Фонтан"
                        await send_message(session, message_text)

                # Сохраняем отправленные ссылки после каждой проверки
                save_sent_list(list(sent_set))
                await asyncio.sleep(random.randint(5, 15))

# Основная функция
async def main():
    sem = asyncio.Semaphore(5)  # Ограничение на количество параллельных запросов
    sent_set = set(load_sent_list())  # Загружаем уже отправленные ссылки

    while True:
        await check_news(sem, sent_set)  # Проверка новостей
        await asyncio.sleep(1111)  # Пауза между проверками (21 минута)

if __name__ == '__main__':
    asyncio.run(main())  # Запускаем основную функцию

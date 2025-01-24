import os
import json
import logging
import aiohttp
import asyncio
import random
from bs4 import BeautifulSoup

# Настройка логгера
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)s]: %(message)s",
                    handlers=[logging.StreamHandler()])

# Загружаем переменные среды
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_LIST_FILE = 'dump.json'

# Определяем ключевые слова для поиска
KEYWORDS = [
    "открытие фонтана 2025",
    "открытие фонтана 2026",
    "строительство фонтана 2025"
]

# Определяем слова, которые должны присутствовать и игнорироваться
MUST_HAVE_WORDS = {"фонтан", "светомузыкальн", "фонтана"}
IGNORE_WORDS = {"канализ", "нефть", "Объявления"}
IGNORE_SITES = {"instagram", "livejournal", "avito"}

# Пользовательские агенты для запросов
user_agents = [
        "Mozilla/5.0 (Windows NT 6.1; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Mozilla/5.0 (Android 12; Mobile; rv:109.0) Gecko/113.0 Firefox/113.0",
        "Opera/9.80 (X11; Linux i686; Ubuntu/14.10) Presto/2.12.388 Version/12.16",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20130331 Firefox/21.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/113.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; OpenBSD i386) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
        "Mozilla/5.0 (X11; CrOS i686 4319.74.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
        "Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko ) Version/5.1 Mobile/9B176 Safari/7534.48.3",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35",
]

# Функция для загрузки отправленных URL
def load_sent_list():
    try:
        with open(SENT_LIST_FILE, 'r', encoding='utf-8') as file:
            return set(json.load(file))
    except FileNotFoundError:
        return set()

# Функция для сохранения отправленных URL
def save_sent_list(sent_list):
    with open(SENT_LIST_FILE, 'w', encoding='utf-8') as file:
        json.dump(list(sent_list), file)

# Функция для очистки URL
def clean_url(link):
    if link.startswith("http"):
        return link
    return f'https://yandex.ru{link}'

# Функция для отправки сообщения в Telegram
async def send_telegram_message(message_text):
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"chat_id": CHANNEL_ID, "text": message_text}) as response:
            if response.status != 200:
                logging.error(f'Ошибка отправки сообщения #fontan: {response.status} - {await response.text()}')

# Функция для поиска новостей на Yandex
async def search_yandex(session, keyword):
    results = []
    query = f'https://yandex.ru/search/?text={keyword}&within=77'
    headers = {'User-Agent': random.choice(user_agents)}

    try:
        async with session.get(query, headers=headers) as response:
            if response.status != 200:
                logging.error(f'Ошибка при обращении к #fontan: {response.status} для запроса: {query}')
                return results
            
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')

            for item in soup.find_all('a', href=True):
                title = item.get_text()
                link = clean_url(item['href'])

                # Проверяем игнорируемые слова и сайты
                if any(word in title for word in IGNORE_WORDS):
                    logging.info(f'Найдено игнорируемое слово #fontan: {title}')
                    continue
                if any(site in link for site in IGNORE_SITES):
                    logging.info(f'Найден игнорируемый сайт #fontan: {link}')
                    continue

                # Проверяем наличие обязательных слов
                if not any(word in title.lower() for word in MUST_HAVE_WORDS):

                    continue
                
                try:
                    async with session.head(link) as link_response:
                        if link_response.status == 200:
                            results.append({'title': title, 'link': link})
                        else:
                            logging.info(f'Ссылка не рабочая #fontan: {link}')
                except Exception as e:
                    logging.warning(f'Проблема с доступом к ссылке #fontan: {link} - {e}')

    except Exception as e:
        logging.error(f'Ошибка при обращении к #fontan: {e}')
    
    logging.info(f'Найдено {len(results)} результатов для {keyword} в #fontan.')
    return results

# Основная функция для мониторинга новостей
async def main():
    sent_set = load_sent_list()

    async with aiohttp.ClientSession() as session:
        while True:
            random_keyword = random.choice(KEYWORDS)  # Выбор случайного ключевого слова
            logging.info(f'Искать по ключевому слову: {random_keyword}')
            
            news_from_yandex = await search_yandex(session, random_keyword)

            # Обработка и отправка найденных новостей
            for news in news_from_yandex:
                if news['link'] not in sent_set:
                    message_text_yandex = f"{news['title']}\n{news['link']}\n⛲@MonitoringFontan📰#fontan"
                    await send_telegram_message(message_text_yandex)
                    sent_set.add(news['link'])
                    logging.info(f'Отправлено сообщение: {message_text_yandex}')
                    await asyncio.sleep(random.randint(5, 15))  # Случайная задержка между сообщениями

            save_sent_list(sent_set)
            await asyncio.sleep(777)  # Ожидание перед следующим циклом

if __name__ == "__main__":
    asyncio.run(main())

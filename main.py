import os
import logging
import random
import aiohttp
import asyncio
import json
from bs4 import BeautifulSoup

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Получение токена API и ID канала из переменных окружения
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_LIST_FILE = 'dump.json'  # Файл для хранения отправленных новостей

# Ключевые слова
KEYWORDS = [
    "открытие фонтанов",
    "открытие фонтанов 2025",
    "открытие музыкального фонтана"
]

# Игнорируемые слова и сайты
IGNORE_WORDS = {"нефть", "недр", "месторождение"}
IGNORE_SITES = {"instagram", "livejournal", "fontanka"}


def clean_url(url):
    """Очищает URL от '/url?q=' и лишних параметров."""
    if url.startswith('/url?q='):
        url = url[len('/url?q='):]
    if '&sa=U&ved' in url:
        url = url.split('&sa=U&ved')[0]
    return url


async def load_sent_news():
    """Загрузка отправленных новостей из файла или создание нового файла, если его нет."""
    if os.path.exists(SENT_LIST_FILE):
        try:
            with open(SENT_LIST_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("Ошибка при загрузке отправленных новостей, создается новый список.")
            return []  # Если файл не существует или пуст, возвращаем пустой список
    return []  # Если файл не существует, возвращаем пустой список


async def save_sent_news(sent_news):
    """Сохранение отправленных новостей в файл."""
    with open(SENT_LIST_FILE, 'w', encoding='utf-8') as file:
        json.dump(sent_news, file)


async def search_google(session, keyword):
    """Поиск новостей на Google по заданному запросу."""
    query = f'https://www.google.ru/search?q={keyword}&hl=ru&tbs=qdr:d'
    async with session.get(query) as response:
        response.raise_for_status()
        soup = BeautifulSoup(await response.text(), 'html.parser')
        news = []

        # Найдем заголовки новостей и ссылки
        for item in soup.find_all('h3'):
            title = item.get_text()
            link = item.find_parent('a')['href']
            cleaned_link = clean_url(link)

            # Добавляем новость
            news.append({'title': title, 'link': cleaned_link})

        logging.debug(f"Найдено новостей по запросу '{keyword}': {len(news)}")
        return news


async def search_yandex(session, keyword):
    """Поиск новостей на Yandex по заданному запросу."""
    query = f'https://yandex.ru/search/?text={keyword}&within=77'
    
    try:
        async with session.get(query) as response:
            response.raise_for_status()
            soup = BeautifulSoup(await response.text(), 'html.parser')
            news = []

            # Найдем заголовки новостей и ссылки
            for item in soup.find_all('h3'):
                title = item.get_text()
                link = item.find_parent('a')['href']
                cleaned_link = clean_url(link)


                # Добавляем новость
                news.append({'title': title, 'link': cleaned_link})

            logging.debug(f"Найдено новостей по запросу '{keyword}': {len(news)}")
            return news

    except aiohttp.ClientResponseError as e:
        logging.error(f"Ошибка при запросе к Yandex по ключевому слову '{keyword}': {e}")
        return []  # Возвращаем пустой список при возникновении ошибки


async def send_message(text):
    """Отправка сообщения в канал."""
    async with aiohttp.ClientSession() as session:
        url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
        payload = {
            'chat_id': CHANNEL_ID,
            'text': text,
            'parse_mode': 'HTML'
        }
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            logging.info("Сообщение успешно отправлено.")
            return True


async def send_random_news():
    """Отправляет одну случайную новость в канал."""
    sent_news = await load_sent_news()  # Загружаем уже отправленные новости
    sent_titles = {item['title'] for item in sent_news}  # Используем множество для более быстрой проверки

    async with aiohttp.ClientSession() as session:
        for keyword in KEYWORDS:
            news_from_google = await search_google(session, keyword)  # Поиск на Google
            news_from_yandex = await search_yandex(session, keyword)  # Поиск на Yandex

            # Объединяем новости из обоих источников
            all_news = news_from_google + news_from_yandex

            # Фильтруем новости по заголовкам, запрещенным словам и сайтам
            filtered_news = []
            for item in all_news:
                title = item['title']
                link = item['link']
                site = link.split('/')[2]  # Извлекаем домен из ссылки

                # Проверяем на наличие запрещенных слов и сайтов
                if title not in sent_titles and not any(word in title.lower() for word in IGNORE_WORDS) and not any(site in link for site in IGNORE_SITES):
                    filtered_news.append(item)

            if filtered_news:
                random_news = random.choice(filtered_news)
                title = random_news['title']
                link = random_news['link']

                # Формируем текст сообщения с хештегами
                message_text = f"{title}\n{link}\n⛲@MonitoringFontan    📰#MonitoringFontan"

                # Отправка сообщения
                if await send_message(message_text):
                    # Сохраняем отправленную новость
                    sent_news.append({'title': title, 'link': link})
                    await save_sent_news(sent_news)
                    logging.info(f"Отправлена новость: {title}")


async def main():
    """Главная функция для периодического запуска."""
    while True:
        await send_random_news()  # Отправляем новости
        await asyncio.sleep(300)  # Пауза перед следующим запросом (5 минут)


if __name__ == '__main__':
    asyncio.run(main())

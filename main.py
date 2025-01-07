import logging
import random
import requests
from bs4 import BeautifulSoup
import json
import time
import os

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
LOG_FILE = 'sent_news.json'
GOOGLE_SEARCH_URL = 'https://www.google.com/search?q={}'

# Настройка логирования
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.FileHandler('news_bot.log'), logging.StreamHandler()]
)

def load_sent_news():
    """Загружает отправленные новости из файла JSON."""
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logger.warning(f"Файл {LOG_FILE} не найден. Создаю новый...")
        return []

def save_sent_news(sent_news):
    """Сохраняет список отправленных новостей в файл JSON."""
    with open(LOG_FILE, 'w', encoding='utf-8') as file:
        json.dump(sent_news, file)

def search_news(query):
    """Поиск новостей на Google по заданному запросу."""
    response = requests.get(GOOGLE_SEARCH_URL.format(query), headers={'User-Agent': 'Mozilla/5.0'})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    news = []
    
    # Измените селектор, если структура Google изменится
    for item in soup.find_all('h3'):
        title = item.get_text()
        link = item.find_parent('a')['href']  # Получаем ссылку на новость
        news.append({'title': title, 'link': link})

    return news

def check_link_validity(link):
    """Проверяет доступность ссылки."""
    try:
        response = requests.head(link, timeout=10)
        if response.status_code < 400:
            return True
        else:
            logger.warning(f"Ссылка {link} возвращает статус-код {response.status_code}. Ссылка недействительна.")
            return False
    except Exception as e:
        logger.exception(f"Произошла ошибка при проверке доступности ссылки {link}: {str(e)}")
        return False

def send_message(text):
    """Отправка сообщения в канал."""
    url = f"https://api.telegram.org/bot{API_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHANNEL_ID,
        'text': text,
        'parse_mode': 'HTML'  # Используйте HTML для форматирования
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка отправки сообщения: {e}")

def send_random_news():
    """Отправляет одну случайную новость в канал."""
    sent_news = load_sent_news()

    # Ключевые слова для поиска
    keywords = "новости доллар"
    news = search_news(keywords)

    # Фильтруем новости, которые уже были отправлены
    new_news = [item for item in news if item['link'] not in sent_news]

    if new_news:
        random_news = random.choice(new_news)
        title = random_news['title']
        link = random_news['link']
        
        # Проверяем работоспособность ссылки
        if check_link_validity(link):
            # Формируем текст сообщения
            message_text = f"<b>{title}</b>\n{link}"

            # Отправка сообщения
            send_message(message_text)

            # Добавляем в список отправленных новостей
            sent_news.append(link)
            save_sent_news(sent_news)
            logger.info(f"Отправлена новость: {title}")
        else:
            logger.warning(f"Новость '{title}' имеет недействительную ссылку. Пропускаю...")
    else:
        logger.info("Нет новых новостей для отправки.")

if __name__ == '__main__':
    while True:
        send_random_news()
        time.sleep(200)  # Пауза перед следующим запросом

import logging
import random
import requests
from bs4 import BeautifulSoup
import json
import time
from datetime import datetime
import os
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
LOG_FILE = 'sent_news.json'
BASE_URL = 'https://duckduckgo.com/'

# Настройка логирования
logging.basicConfig(level=logging.INFO)

def load_sent_news():
    """Загружает отправленные новости из файла JSON."""
    try:
        with open(LOG_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_sent_news(sent_news):
    """Сохраняет список отправленных новостей в файл JSON."""
    with open(LOG_FILE, 'w') as file:
        json.dump(sent_news, file)

def search_news(query):
    """Поиск новостей на DuckDuckGo по заданному запросу."""
    params = {'q': query}
    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    news = []
    
    # Подгоните селекторы под HTML-структуру DuckDuckGo, если они изменятся
    for item in soup.find_all('a', class_='result__link'):
        title = item.get_text()
        link = item['href']
        news.append({'title': title, 'link': link})
    
    return news

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
        logging.error(f"Ошибка отправки сообщения: {e}")

def send_random_news():
    """Отправляет одну случайную новость в канал."""
    sent_news = load_sent_news()
    today_date = datetime.now().strftime("%d.%m.%Y")

    # Формируем ключевые слова для поиска
    keywords = [
        f"фонтан ростов {today_date}",
        f"фонтан строительство {today_date}"
    ]

    news = []
    for keyword in keywords:
        news += search_news(keyword)

    # Фильтруем новости, которые уже были отправлены
    new_news = [item for item in news if item['link'] not in sent_news]

    if new_news:
        random_news = random.choice(new_news)
        title = random_news['title']
        link = random_news['link']

        # Формируем текст сообщения
        message_text = f"<b>{title}</b>\n{link}"

        # Отправка сообщения
        send_message(message_text)

        # Добавление в список отправленных новостей
        sent_news.append(link)
        save_sent_news(sent_news)
        logging.info(f"Отправлена новость: {title}")
    else:
        logging.info("Нет новых новостей для отправки.")

if __name__ == '__main__':
    while True:
        send_random_news()
        time.sleep(200)  # Пауза перед следующим запросом

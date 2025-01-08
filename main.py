import logging
import random
import requests
import re
from bs4 import BeautifulSoup
import json
import time
import os

API_TOKEN = os.getenv("API_TOKEN")

CHANNEL_ID = os.getenv("CHANNEL_ID")
LOG_FILE = 'sent_news.json'  # Файл для сохранения отправленных новостей
GOOGLE_SEARCH_URL = 'https://www.google.ru/search?q={}'

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def load_sent_news():
    """Загружает отправленные новости из файла JSON."""
    try:
        with open(LOG_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.info("Файл с отправленными новостями не найден. Создание нового файла.")
        return []

def save_sent_news(sent_news):
    """Сохраняет список отправленных новостей в файл JSON."""
    with open(LOG_FILE, 'w') as file:
        json.dump(sent_news, file)
        logging.info("Сохранены отправленные новости в файл.")

def clean_url(url):
    """Очищает URL от лишних параметров после '&sa=U&ved'."""
    # Удаляем все, что идет после и включая '&sa=U&ved'
    if '&sa=U&ved' in url:
        cleaned_url = url.split('&sa=U&ved')[0]
    else:
        cleaned_url = url
    return cleaned_url

def search_news(query):
    """Поиск новостей на Google по заданному запросу."""
    response = requests.get(GOOGLE_SEARCH_URL.format(query))
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    news = []

    # Измените селекторы, если структура Google изменится
    for item in soup.find_all('h3'):
        title = item.get_text()
        link = item.find_parent('a')['href']  # Получаем ссылку на новость
        cleaned_link = clean_url(link)  # Очищаем ссылку
        news.append({'title': title, 'link': cleaned_link})

    logging.debug(f"Найдено новостей: {len(news)}")
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
        logging.info("Сообщение успешно отправлено.")
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка отправки сообщения: {e}")

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

        # Формируем текст сообщения
        message_text = f"{title}\n{link}"

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

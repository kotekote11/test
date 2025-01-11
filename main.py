import logging
import random
import requests
import json
import time
from bs4 import BeautifulSoup
import os

API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
KEYWORDS = "фонтан открытие"  # Ваши ключевые слова
SENT_LIST_FILE = 'sent_news.json'  # Файл для хранения отправленных новостей

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def clean_url(url):
    """Очищает URL от '/url?q=' и лишних параметров после '&sa=U&ved'."""
    if url.startswith('/url?q='):
        url = url[len('/url?q='):]
    if '&sa=U&ved' in url:
        url = url.split('&sa=U&ved')[0]
    return url

def load_sent_news():
    """Загружает уже отправленные новости из файла."""
    try:
        with open(SENT_LIST_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []  # Если файл не существует или пуст, возвращаем пустой список

def save_sent_news(sent_news):
    """Сохраняет уже отправленные новости в файл."""
    with open(SENT_LIST_FILE, 'w') as file:
        json.dump(sent_news, file)

def search_news():
    """Поиск новостей на Google по заданному запросу."""
    query = f'https://www.google.ru/search?q={KEYWORDS}&hl=ru&tbs=qdr:d'  # Поиск за последний день
    response = requests.get(query)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    news = []

    # Найдем заголовки новостей и ссылки
    for item in soup.find_all('h3'):
        title = item.get_text()
        link = item.find_parent('a')['href']
        cleaned_link = clean_url(link)
        
        # Проверяем, что ссылка рабочая
        try:
            if requests.head(cleaned_link).status_code == 200:
                news.append({'title': title, 'link': cleaned_link})
        except requests.exceptions.RequestException:
            logging.warning(f"Некорректная ссылка: {cleaned_link}")

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
        return True
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка отправки сообщения: {e}")
        return False

def send_random_news():
    """Отправляет одну случайную новость в канал."""
    news = search_news()

    # Загружаем уже отправленные новости
    sent_news = load_sent_news()
    sent_titles = [item['title'] for item in sent_news]

    # Фильтруем новости по заголовкам
    new_news = [item for item in news if item['title'] not in sent_titles]

    if new_news:
        random_news = random.choice(new_news)
        title = random_news['title']
        link = random_news['link']
        
        # Формируем текст сообщения с хештегом #fontan
        message_text = f"{title}\n{link}\n\n#fontan"

        # Отправка сообщения

        if send_message(message_text):
            # Сохраняем отправленную новость
            sent_news.append({'title': title, 'link': link})

            save_sent_news(sent_news)
            logging.info(f"Отправлена новость: {title}")
    else:
        logging.info("Нет новых новостей для отправки.")

def cleanup_sent_news(num_of_iterations):
    """Очищает файл, оставляя только последние 3 записи каждые 90 итераций."""
    if num_of_iterations % 90 == 0:
        sent_news = load_sent_news()  # Загружаем все отправленные новости
        if len(sent_news) > 3:
            send_news_to_keep = sent_news[-3:]  # Храним только последние 3 записи
            save_sent_news(send_news_to_keep)  # Сохраняем их в файл
            logging.info("Очистка старых новостей завершена, оставлены только последние 3 записи.")

if __name__ == '__main__':
    num_iterations = 0
    while True:
        send_random_news()  # Отправляем новости
        num_iterations += 1

        cleanup_sent_news(num_iterations)  # Очищаем старые записи при необходимости

        time.sleep(300)  # Пауза перед следующим запросом (5 минут)

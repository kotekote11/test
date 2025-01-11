import os
import logging
import random
import requests
import json
import time
from bs4 import BeautifulSoup

# Получаем токен API и ID канала из переменных окружения
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_LIST_FILE = 'google.json'  # Файл для хранения отправленных новостей

# Ключевые слова
KEYWORDS = [
    "открытие фонтанов",
    "открытие фонтанов 2025",
    "открытие музыкального фонтана"
]

# Списки игнорирования
IGNORE_WORDS = {"нефть", "недр", "месторождение"}  # Запрещенные слова
IGNORE_SITES = {"instagram", "livejournal", "fontanka"}  # Запрещенные сайты

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
    """Загружает уже отправленные новости из файла или создает файл, если его нет."""
    if os.path.exists(SENT_LIST_FILE):
        try:
            with open(SENT_LIST_FILE, 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            logging.warning("Ошибка при загрузке отправленных новостей, создается новый список.")
            return []  # Если файл не существует или пуст, возвращаем пустой список
    return []  # Если файл не существует, возвращаем пустой список

def save_sent_news(sent_news):
    """Сохраняет уже отправленные новости в файл."""
    with open(SENT_LIST_FILE, 'w') as file:
        json.dump(sent_news, file)

def search_news(keyword):
    """Поиск новостей на Google по заданному запросу."""
    query = f'https://www.google.ru/search?q={keyword}&hl=ru&tbs=qdr:d'  # Поиск за последний день
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

    logging.debug(f"Найдено новостей по запросу '{keyword}': {len(news)}")
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
    sent_news = load_sent_news()  # Загружаем уже отправленные новости

    sent_titles = {item['title'] for item in sent_news}  # Используем множество для более быстрой проверки

    for keyword in KEYWORDS:
        news = search_news(keyword)

        # Фильтруем новости по заголовкам, запрещенным словам и сайтам
        filtered_news = []
        for item in news:
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
            message_text = f"{title}\n{link}\n⛲@MonitoringFontan📰#MonitoringFontan"

            # Отправка сообщения
            if send_message(message_text):
                # Сохраняем отправленную новость
                sent_news.append({'title': title, 'link': link})
                save_sent_news(sent_news)
                logging.info(f"Отправлена новость: {title}")

def cleanup_sent_news(num_of_iterations):
    """Очищает файл, оставляя только последние 9 записей каждые 90 итераций."""
    if num_of_iterations % 90 == 0:
        sent_news = load_sent_news()  # Загружаем все отправленные новости
        if len(sent_news) > 9:
            sent_news = sent_news[-9:]  # Храним только последние 9 записей
            save_sent_news(sent_news)  # Сохраняем их в файл
            logging.info("Очистка старых новостей завершена, оставлены только последние 9 записей.")

if __name__ == '__main__':
    num_iterations = 0
    while True:
        send_random_news()  # Отправляем новости
        num_iterations += 1

        cleanup_sent_news(num_iterations)  # Очищаем старые записи при необходимости

        time.sleep(300)  # Пауза перед следующим запросом (5 минут)

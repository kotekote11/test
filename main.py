import os
import requests
from bs4 import BeautifulSoup
import logging
import json
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
API_TOKEN = os.getenv("API_TOKEN")  # Токен Telegram
CHANNEL_ID = os.getenv("CHANNEL_ID")  # Идентификатор канала
SENT_LIST_FILE = 'google.json'  # Файл для хранения отправленных новостей
KEYWORDS = ["открытие фонтанов", "открытие фонтанов 2025", "открытие музыкального фонтана "]
IGNORE_SITES = ["instagram", "livejournal", "fontanka"]  # Сайты, которые игнорируются
IGNORE_WORDS = ["нефть", "недр", "месторождение"]  # Слова, которые игнорируются

def clean_url(url):
    """Очищает URL, оставляя только нужный адрес."""
    url = url[len('/url?q='):]  # Убираем префикс
    return url.split('&sa=U&ved')[0]  # Убираем лишние параметры

def send_telegram_message(message_text):
    """Отправляет сообщение в Telegram."""
    url = f'https://api.telegram.org/bot{API_TOKEN}/sendMessage'
    data = {
        'chat_id': CHANNEL_ID,
        'text': message_text,
        'parse_mode': 'HTML'
    }
    response = requests.post(url, data=data)
    return response.json()

def search_news():
    """Ищет новости по ключевым словам на Google."""
    query = f'https://www.google.ru/search?q={KEYWORDS}&hl=ru&tbs=qdr:d'  # Поиск за День
    response = requests.get(query)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = []
    for item in soup.find_all('h3'):
        link = item.find_parent('a')  # Получаем родительский элемент <a>
        if link:
            cleaned_link = clean_url(link['href'])
            title = item.get_text(strip=True)

            # Проверяем, не содержится ли в заголовке игнорируемые слова
            if any(word in title.lower() for word in IGNORE_WORDS):
                logging.debug(f'Игнорируем заголовок: {title}')
                continue

            # Проверяем, не принадлежит ли сайт к игнорируемым
            if any(site in cleaned_link for site in IGNORE_SITES):
                logging.debug(f'Игнорируем сайт: {cleaned_link}')
                continue

            if requests.head(cleaned_link).status_code == 200:  # Проверяем доступность ссылки
                news_items.append({'title': title, 'link': cleaned_link})

    return news_items

def load_sent_list():
    """Загружает список отправленных новостей из файла."""
    if os.path.exists(SENT_LIST_FILE):
        with open(SENT_LIST_FILE, 'r') as file:
            return json.load(file)
    return []

def save_sent_list(sent_list):
    """Сохраняет список отправленных новостей в файл."""
    with open(SENT_LIST_FILE, 'w') as file:
        json.dump(sent_list, file)

def main():
    sent_list = load_sent_list()  # Загружаем список отправленных новостей
    repeat_count = 0

    while True:
        news_items = search_news()
        logging.info(f'Найдено {len(news_items)} новостей.')

        for news in news_items:
            if news['link'] not in sent_list:  # Если новость еще не отправлена

                message_text = f"{news['title']}\n{news['link']}\n⛲@MonitoringFontan\n📰#MonitoringFontan"
                send_telegram_message(message_text)
                sent_list.append(news['link'])  # Добавляем ссылку в список отправленных
                logging.info(f'Отправлено: {news["title"]}')

        repeat_count += 1

        # Удаляем все записи в файле, кроме последних 9, каждые 90 повторов
        if repeat_count % 90 == 0:
            sent_list = sent_list[-9:]  # Оставляем только последние 9 записей
            save_sent_list(sent_list)  # Сохраняем обновленный список

        time.sleep(300)  # Пауза 5 минут

if __name__ == "__main__":
    main()

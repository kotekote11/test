import requests
from bs4 import BeautifulSoup
import logging
import json
import time
import os
TELEGRAM_TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("CHANNEL_ID")
# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Конфигурация Telegram
#TELEGRAM_TOKEN = 'YOUR_TELEGRAM_TOKEN'  # Укажите ваш токен Telegram
#CHAT_ID = 'YOUR_CHAT_ID'  # Укажите ваш chat ID

# Файл для хранения отправленных новостей
SENT_NEWS_FILE = 'sent_news.json'

# Ключевые слова для поиска
KEYWORDS = "новости доллар"

# Загрузка отправленных новостей из файла
def load_sent_news():
    try:
        with open(SENT_NEWS_FILE, 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Сохранение отправленных новостей в файл
def save_sent_news(sent_news):
    with open(SENT_NEWS_FILE, 'w') as file:
        json.dump(sent_news, file)

# Отправка сообщения в Telegram
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    response = requests.post(url, data=data)
    return response.json()

# Поиск новостей на Google
def search_news():
    query = f'https://www.google.ru/search?q={KEYWORDS}&hl=ru'
    response = requests.get(query)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_links = []
    for item in soup.find_all('div', class_='BVG0Nb'):
        link = item.find('a')
        if link and link.get('href'):
            news_links.append(link.get('href'))

    return news_links

# Главная логика
def main():
    sent_news = load_sent_news()
    
    news_links = search_news()
    logging.info(f'Найдено {len(news_links)} новостей.')

    # Фильтруем ссылки, которые уже были отправлены
    new_news_links = [link for link in news_links if link not in sent_news]

    if new_news_links:
        # Отправляем первую новость
        selected_news = new_news_links[0]
        message = f'Новая новость: {selected_news}'

        # Отправляем сообщение в Telegram
        response = send_telegram_message(message)
        if response.get('ok'):
            logging.info(f'Отправлено: {selected_news}')
            sent_news.append(selected_news)
            save_sent_news(sent_news)
        else:
            logging.error(f'Ошибка отправки: {response}')
    else:
        logging.info('Нет новых новостей для отправки.')

if __name__ == "__main__":
    while True:
        main()
        time.sleep(200)  # Подождите 200 секунд перед следующим запросом

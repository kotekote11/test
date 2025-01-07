import requests
from bs4 import BeautifulSoup
import logging
import json
import time
import os
TELEGRAM_TOKEN = os.getenv("token")
CHAT_ID = os.getenv("id_channel")

# Настроим логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Конфигурация Telegram
TELEGRAM_TOKEN = 'YOUR_TELEGRAM_TOKEN'  # Укажите ваш токен Telegram
CHAT_ID = 'YOUR_CHAT_ID'  # Ваш chat ID

# Файл для хранения отправленных новостей
SENT_NEWS_FILE = 'sent_news.json'

# Ключевые слова для поиска
SEARCH_TERMS = ['новости недвижимости', 'новости доллар']

# Загрузка отправленных новостей из файла
def load_sent_news():
    try:
        with open(SENT_NEWS_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Сохранение отправленных новостей в файл
def save_sent_news(sent_news):
    with open(SENT_NEWS_FILE, 'w') as f:
        json.dump(sent_news, f)

# Отправка сообщения в Telegram
def send_telegram_message(message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    response = requests.post(url, data=data)
    return response.json()

# Поиск новостей
def search_news():
    today = time.strftime('%Y-%m-%d')
    query = '+'.join(SEARCH_TERMS) + f'+{today}'
    url = f'https://www.google.ru/search?q={query}'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим все ссылки на результаты поиска
    news_links = []
    for item in soup.find_all('div', class_='BVG0Nb'):
        link = item.find('a')
        if link and link.get('href'):
            news_links.append(link.get('href'))

    return news_links

# Главная логика работы
def main():
    sent_news = load_sent_news()
    
    news_links = search_news()
    logging.info(f'Найдено {len(news_links)} новостей.')

    # Фильтруем ссылки, которые уже были отправлены
    new_news_links = [link for link in news_links if link not in sent_news]

    if new_news_links:
        # Выбор случайной новости
        selected_news = new_news_links[0]  # Отправим первую новость для примера
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

import requests
from bs4 import BeautifulSoup
import json
import logging
import time
import os

YOUR_BOT_TOKEN = os.getenv("API_TOKEN")

CHAT_ID = os.getenv("CHANNEL_ID")
# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Конфигурация Telegram API
TELEGRAM_API_URL = 'https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage'

# Функция для отправки сообщения в Telegram
def send_telegram_message(message):
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(TELEGRAM_API_URL, json=payload)
    if response.status_code == 200:
        logging.info("Сообщение отправлено в Telegram.")
    else:
        logging.error("Ошибка при отправке сообщения: %s", response.text)

# Функция для парсинга новостей
def parse_news():
    url = 'https://www.google.ru/search?q=новости+доллар'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    news_items = []
    for item in soup.find_all('div', class_='BVG0Nb'):
        title = item.get_text()
        link = item.find('a')['href']
        news_items.append({'title': title, 'link': link})

    return news_items

# Загрузка ранее отправленных новостей
def load_sent_news(filename='sent_news.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Сохранение отправленных новостей
def save_sent_news(sent_news, filename='sent_news.json'):
    with open(filename, 'w') as file:
        json.dump(sent_news, file)

# Основная функция
def main():
    sent_news = load_sent_news()
    
    while True:
        news = parse_news()
        new_news = [item for item in news if item['link'] not in sent_news]

        for item in new_news:
            message = f"Новая новость: {item['title']} \nСсылка: {item['link']}"
            send_telegram_message(message)
            sent_news.append(item['link'])  # Добавляем ссылку в список отправленных новостей

        save_sent_news(sent_news)  # Сохраняем обновленный список отправленных новостей
        time.sleep(200)  # Ждем 200 секунд перед следующей проверкой

if __name__ == "__main__":
    main()

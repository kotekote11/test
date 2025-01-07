import requests
from bs4 import BeautifulSoup
import logging
import json
import time
import os

YOUR_BOT_TOKEN = os.getenv("API_TOKEN")

CHAT_ID = os.getenv("CHANNEL_ID")
# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# URL для парсинга и API Telegram
URL = 'https://www.google.ru/search?q=новости+доллар'
TELEGRAM_API = 'https://api.telegram.org/bot<YOUR_BOT_TOKEN>/sendMessage'

# Загрузка отправленных новостей
def load_sent_news():
    try:
        with open('sent_news.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Сохранение отправленных новостей
def save_sent_news(sent_news):
    with open('sent_news.json', 'w', encoding='utf-8') as file:
        json.dump(sent_news, file)

# Функция для парсинга новостей
def parse_news():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    news = []
    for item in soup.find_all('div', class_='BVG0Nb'):
        title = item.find('h3').text
        link = item.find('a')['href']
        news.append({'title': title, 'link': link})
    
    return news

# Отправка новостей в Telegram
def send_news(news):
    for item in news:
        payload = {
            'chat_id': CHAT_ID,
            'text': f"{item['title']}\n{item['link']}"
        }
        response = requests.post(TELEGRAM_API, json=payload)
        if response.status_code == 200:
            logging.info(f"Отправлено: {item['title']}")
        else:
            logging.error("Ошибка при отправке: " + response.text)

# Основная функция
def main():
    sent_news = load_sent_news()
    while True:
        news = parse_news()
        new_news = [item for item in news if item['link'] not in sent_news]
        
        if new_news:
            send_news(new_news)
            sent_news.extend(item['link'] for item in new_news)
            save_sent_news(sent_news)
        
        logging.info("Ожидание новых новостей...")
        time.sleep(200)  # пауза 200 секунд

if __name__ == '__main__':
    main()

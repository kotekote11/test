import requests
from bs4 import BeautifulSoup
import logging
import json
import time
import os

bot_token = os.getenv("API_TOKEN")

chat_id = os.getenv("CHANNEL_ID")
# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Функция для выполнения запроса к Google и парсинга новостей
def fetch_news(keywords):
    logging.info(f'Запрос новостей по ключевым словам: {keywords}')
    url = f"https://www.google.ru/search?q={keywords}&tbm=nws"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Проверка на наличие ошибок
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_items = []
        for item in soup.select('h3'):
            news_items.append(item.get_text())
        
        return news_items
    except Exception as e:
        logging.error(f'Ошибка при запросе: {e}')
        return []

# Функция для отправки новостей в Telegram
def send_to_telegram(news):
    #bot_token = 'YOUR_BOT_TOKEN'
    #chat_id = 'YOUR_CHAT_ID'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    
    for news_item in news:
        requests.post(url, data={'chat_id': chat_id, 'text': news_item})
        logging.info(f'Отправлено в Telegram: {news_item}')

def main():
    keywords = "новости доллар"
    
    while True:
        news = fetch_news(keywords)
        
        if news:
            send_to_telegram(news)
        
        # Сохранение новостей в файл в формате JSON
        with open('news.json', 'w', encoding='utf-8') as file:
            json.dump(news, file, ensure_ascii=False, indent=4)
            logging.info('Новости сохранены в news.json')
        
        # Пауза на 200 секунд
        logging.info('Ожидание перед следующим запросом...')
        time.sleep(200)

if __name__ == "__main__":
    main()

import requests
from bs4 import BeautifulSoup
import logging
import time
import os

bot_token = os.getenv("API_TOKEN")

chat_id = os.getenv("CHANNEL_ID")
# Настройка логирования
logging.basicConfig(level=logging.DEBUG)

# Функция для очистки URL
def clean_url(url):
    url = url[len('/url?q='):]
    url = url.split('&sa=U&ved')[0]
    return url

# Функция для получения новостей из Google
def get_news(keywords):
    search_url = f"https://www.google.ru/search?q={keywords}&num=10"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    news_items = []
    for item in soup.find_all('h3'):
        title = item.get_text()
        link = item.find_parent('a')['href']
        clean_link = clean_url(link)
        news_items.append((title, clean_link))
    
    return news_items

# Функция для проверки на дублирование
def check_duplicates(news_items, existing_titles):
    new_news = []
    for title, link in news_items:
        if title not in existing_titles:
            new_news.append((title, link))
    return new_news

# Функция для отправки новостей в Telegram
def send_to_telegram(news_items, bot_token, chat_id):
    for title, link in news_items:
        message = f"{title}\n{link}"
        response = requests.post(f"https://api.telegram.org/bot{bot_token}/sendMessage", 
                                 data={'chat_id': chat_id, 'text': message})
        if response.status_code == 200:
            logging.debug(f"Sent: {message}")
        else:
            logging.error(f"Failed to send message: {response.text}")

# Основной процесс
def main():
    keywords = "новости евро"
    
    # Получаем существующие новости из Telegram канала
    existing_titles = set()  # Здесь должен быть код для получения заголовков из канала

    while True:
        news_items = get_news(keywords)
        new_news = check_duplicates(news_items, existing_titles)
        
        if new_news:
            send_to_telegram(new_news, bot_token, chat_id)
        
        time.sleep(200)  # Пауза перед следующим запросом

if __name__ == "__main__":
    main()

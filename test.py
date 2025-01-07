import requests
from bs4 import BeautifulSoup
import logging
import json
import time
import os
TELEGRAM_BOT_TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("CHANNEL_ID")
# Настройка логгирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ваши данные для работы с Telegram Bot API
#TELEGRAM_BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
#CHAT_ID = 'YOUR_CHAT_ID'  # ID чата, куда будут отправляться сообщения

# URL для поиска новостей
BASE_URL = 'https://news.google.com/'
SEARCH_URL = BASE_URL + '?q={}&hl=ru&gl=RU&ceid=RU%3Aru'

# Ключевое слово для поиска
KEYWORD = 'новости доллар'

# Файл для хранения уже отправленных новостей
SENT_NEWS_FILE = 'sent_news.json'

def get_latest_news(keyword):
    """Получает последние новости по ключевому слову."""
    url = SEARCH_URL.format(keyword)
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        
        news_list = []
        for article in soup.find_all('article'):
            title_tag = article.find('h3', class_='ipQwMb ekueJc gEAtD c0vUI')
            link_tag = article.find('a', class_='VDXfz')
            
            if title_tag and link_tag:
                title = title_tag.text.strip()
                link = BASE_URL[:-1] + link_tag['href']
                
                news_item = {
                    'title': title,
                    'link': link
                }
                news_list.append(news_item)
        
        return news_list[:1]
    else:
        logger.error(f'Ошибка при получении страницы: {response.status_code}')
        return None

def load_sent_news():
    """Загружает список уже отправленных новостей из файла."""
    try:
        with open(SENT_NEWS_FILE, 'r') as f:
            sent_news = json.load(f)
    except FileNotFoundError:
        sent_news = {}
    return sent_news

def save_sent_news(sent_news):
    """Сохраняет список уже отправленных новостей в файл."""
    with open(SENT_NEWS_FILE, 'w') as f:
        json.dump(sent_news, f)

def send_message(text):
    """Отправляет сообщение в Telegram чат."""
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {'chat_id': CHAT_ID, 'text': text}
    response = requests.post(url, data=data)
    if response.status_code != 200:
        logger.error(f'Ошибка при отправке сообщения: {response.status_code}')

def main():
    # Загрузка списка уже отправленных новостей
    sent_news = load_sent_news()
    
    # Получение последних новостей
    latest_news = get_latest_news(KEYWORD)
    
    if latest_news is not None:
        for news in latest_news:
            news_title = news['title']
            news_link = news['link']
            news_hash = hash((news_title, news_link))
            
            if str(news_hash) not in sent_news:
                message_text = f'{news_title}\n{news_link}'
                send_message(message_text)
                sent_news[str(news_hash)] = True
                logger.info(f'Новость "{news_title}" успешно отправлена.')
    
    # Сохраняем обновленный список отправленных новостей
    save_sent_news(sent_news)

if __name__ == '__main__':
    while True:
        main()
        time.sleep(200)  # Пауза между проверками (примерно каждые 3 минуты)

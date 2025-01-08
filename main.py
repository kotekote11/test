import requests
from bs4 import BeautifulSoup
import logging
import telegram
from telegram.ext import Updater, CommandHandler
import time
import os

token = os.getenv("API_TOKEN")

chat_id = os.getenv("CHANNEL_ID")
# Настройка логирования
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Функция для очистки URL от лишних параметров
def clean_url(url):
    url = url[len('/url?q='):]
    url = url.split('&sa=U&ved')[0]
    return url

# Парсер Google News
def parse_google_news(keywords):
    url = f'https://news.google.com/search?q={keywords}&hl=ru&gl=RU&ceid=RU%3Aru'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    news_list = []
    for item in soup.find_all('article'):
        try:
            title = item.find('h3').get_text()
            link = item.find('a', href=True)['href']
            cleaned_link = clean_url(link)
            news_list.append((title, cleaned_link))
        except AttributeError:
            continue
        
    return news_list

# Проверка наличия новости на канале Telegram
def check_if_exists(title, bot, chat_id):
    offset = 0
    limit = 100
    while True:
        updates = bot.get_updates(offset=offset, timeout=10, allowed_updates=['channel_post'])
        for update in updates:
            if update.channel_post.text == title:
                logger.info(f"Новость '{title}' уже существует.")
                return True
            
        # Если достигли лимита сообщений, то прерываемся
        if len(updates) < limit:
            break
        
        offset += limit
    
    return False

# Отправка новой уникальной новости в канал Telegram
def send_new_news(news_list, bot, chat_id):
    for title, link in news_list:
        if not check_if_exists(title, bot, chat_id):
            message = f"{title}\n{link}"
            bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"Отправлена новая новость: {title}")

# Основная функция программы
def main():

    bot = telegram.Bot(token=token)
    
    # ID канала Telegram, куда будут отправляться новости

    
    # Ключевое слово для поиска новостей
    keywords = "новости евро"
    
    while True:
        news_list = parse_google_news(keywords)
        send_new_news(news_list, bot, chat_id)
        time.sleep(600)  # Пауза между проверками (10 минут)

if __name__ == '__main__':
    main()

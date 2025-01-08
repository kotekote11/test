
import requests
from bs4 import BeautifulSoup
import logging
import time
import os

telegram_token = os.getenv("API_TOKEN")

telegram_chat_id = os.getenv("CHANNEL_ID")
# Настройка логгирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Функция для очистки URL от лишних параметров
def clean_url(url):
    url = url[len('/url?q='):]
    url = url.split('&sa=U&ved')[0]
    return url

# Функция для получения списка ссылок на канал
def get_channel_links():
    response = requests.get("https://t.me/s/fgtestfg")
    soup = BeautifulSoup(response.text, 'html.parser')
    
    links = []
    for tag in soup.find_all('a', class_='tgme_widget_message_link_preview'):
        link = tag['href']
        if link.startswith('http'):
            links.append(link)
            
    logger.debug(f'Получено {len(links)} ссылок с канала.')
    return links

# Функция для поиска новостей на Google News
def search_google_news(keywords):
    url = f"https://news.google.com/search?q={keywords}&hl=ru"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    news_list = []
    for h3_tag in soup.find_all('h3'):
        a_tag = h3_tag.find('a')
        if a_tag and a_tag.has_attr('href'):
            link = clean_url(a_tag['href'])
            title = a_tag.text.strip()
            news_list.append((title, link))
    
    logger.debug(f'Найдено {len(news_list)} новостей на Google News.')
    return news_list

# Функция для фильтрации новых новостей
def filter_new_news(channel_links, google_news):
    new_news = []
    for title, link in google_news:
        if link not in channel_links:
            new_news.append((title, link))
    
    logger.debug(f'{len(new_news)} новостей являются новыми.')
    return new_news

# Функция для отправки сообщений через Telegram Bot API
def send_to_telegram_bot(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={message}"
    response = requests.get(url)
    if response.status_code == 200:
        logger.info(f"Сообщение успешно отправлено: {message}")
    else:
        logger.error(f"Произошла ошибка при отправке сообщения: {response.text}")

if __name__ == "__main__":

    keywords = "новости рубля"
    
    # Получаем список ссылок с канала
    channel_links = get_channel_links()
    
    # Ищем новости на Google News
    google_news = search_google_news(keywords)
    
    # Фильтруем новые новости
    new_news = filter_new_news(channel_links, google_news)
    
    # Отправляем новые новости через Telegram Bot
    for title, link in new_news:
        message = f"{title}\n{link}"
        send_to_telegram_bot(telegram_token, telegram_chat_id, message)
        
    # Пауза перед следующим запуском (например, каждые 5 минут)
    time.sleep(200)

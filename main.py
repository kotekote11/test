import requests
from bs4 import BeautifulSoup
import logging
import json
import time
import os

TELEGRAM_TOKEN = os.getenv("API_TOKEN")

CHAT_ID = os.getenv("CHANNEL_ID")
# Configure logging
logging.basicConfig(level=logging.DEBUG)

TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

# Function to clean URLs
def clean_url(url):
    url = url[len('/url?q='):]  # Remove '/url?q=' prefix
    url = url.split('&sa=U&ved')[0]  # Remove tracking parameters
    return url

# Function to scrape news articles
def scrape_news(keywords):
    search_url = f'https://www.google.ru/search?q={"+".join(keywords.split())}&hl=ru'
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    news = []
    for item in soup.find_all('h3'):
        link = item.find_parent('a')['href']
        title = item.get_text()
        cleaned_link = clean_url(link)
        news.append({'title': title, 'link': cleaned_link})

    return news

# Function to check if title exists in the Telegram channel
def check_existing_titles(channel_url):
    response = requests.get(channel_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    existing_titles = {item.get_text() for item in soup.find_all('a', class_='tgme_widget_message_text')}
    return existing_titles

# Function to send message to Telegram
def send_telegram_message(message):
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(TELEGRAM_API_URL, json=payload)
    return response.ok

def main():
    keywords = "новости евро"
    channel_url = 'https://t.me/s/fgtestfg'  # URL of the Telegram channel
    existing_titles = check_existing_titles(channel_url)

    while True:
        logging.debug("Scraping news...")
        news = scrape_news(keywords)
        new_news = [item for item in news if item['title'] not in existing_titles]

        for item in new_news:
            message = f"{item['title']}\n{item['link']}"
            if send_telegram_message(message):
                logging.info(f"Sent message: {message}")
            else:
                logging.error("Failed to send message")

        time.sleep(200)  # Wait for 200 seconds before the next scrape

if __name__ == '__main__':
    main()

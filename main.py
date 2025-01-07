import requests
from bs4 import BeautifulSoup
import logging
import json
import time
import os
BOT_TOKEN = os.getenv("API_TOKEN")
CHAT_ID = os.getenv("CHANNEL_ID")
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# Keywords to search for
keywords = "новости доллар"

# File to store sent news
SENT_NEWS_FILE = 'sent_news.json'

# Function to send message via Telegram bot
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response.json()

# Function to load sent news from file
def load_sent_news():
    try:
        with open(SENT_NEWS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to save sent news to file
def save_sent_news(sent_news):
    with open(SENT_NEWS_FILE, 'w') as file:
        json.dump(sent_news, file)

# Function to scrape news
def scrape_news():
    url = "https://www.google.ru/search?q=" + keywords.replace(" ", "+")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Example: Extract news titles and links (adjust according to actual HTML structure)
    news = []
    for item in soup.find_all('div', class_='news_item_class'):  # Adjust class name
        title = item.find('h3').text
        link = item.find('a')['href']
        news.append({'title': title, 'link': link})

    return news

# Main loop
def main():
    sent_news = load_sent_news()

    while True:
        news = scrape_news()
        new_news = [item for item in news if item['link'] not in sent_news]

        for item in new_news:
            message = f"{item['title']}\\n{item['link']}"
            send_telegram_message(message)
            sent_news.append(item['link'])
            save_sent_news(sent_news)
            logging.info(f"Sent news: {item['title']}")

        time.sleep(200)  # Wait for 200 seconds before next iteration

if __name__ == "__main__":
    main()


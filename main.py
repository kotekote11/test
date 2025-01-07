import requests
from bs4 import BeautifulSoup
import logging
import json
import time
import os

TELEGRAM_BOT_TOKEN = os.getenv("API_TOKEN")

TELEGRAM_CHAT_ID = os.getenv("CHANNEL_ID")
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Keywords for filtering news
keywords = "новости доллар"

# Function to send a message via Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    response = requests.post(url, data=payload)
    return response.json()

# Function to fetch and parse news from DuckDuckGo
def fetch_news():
    url = "https://duckduckgo.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Example parsing logic (this will vary depending on actual page structure)
    news = []
    for item in soup.find_all('div', class_='news-item'):
        title = item.find('h2').text
        link = item.find('a')['href']
        news.append({'title': title, 'link': link})
    
    return news

# Function to load sent news from a JSON file
def load_sent_news(file_path):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Function to save sent news to a JSON file
def save_sent_news(file_path, sent_news):
    with open(file_path, 'w') as file:
        json.dump(sent_news, file)

def main():
    sent_news_file = 'sent_news.json'
    sent_news = load_sent_news(sent_news_file)

    while True:
        logging.info("Fetching news...")
        news = fetch_news()

        # Filter new news items
        new_news = [item for item in news if item['link'] not in sent_news]

        for item in new_news:
            if keywords in item['title']:
                logging.info(f"Sending news: {item['title']}")
                send_telegram_message(f"News: {item['title']}\nLink: {item['link']}")
                sent_news.append(item['link'])

        # Save the updated list of sent news
        save_sent_news(sent_news_file, sent_news)

        # Sleep for 200 seconds
        logging.info("Sleeping for 200 seconds...")
        time.sleep(200)

if __name__ == "__main__":
    main()

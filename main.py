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


# Keywords for news
keywords = "новости доллар"

# Function to send message via Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    response = requests.post(url, json=payload)
    return response.json()

# Function to fetch news from Google
def fetch_news():
    url = "https://www.google.ru/search?q=" + keywords
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract news items (this part needs to be adapted to the actual HTML structure)
    news = []
    for item in soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd'):
        link = item.find_parent('a')['href']
        title = item.get_text()
        news.append({'title': title, 'link': link})
    
    return news

# Load sent news from a file
def load_sent_news():
    try:
        with open('sent_news.json', 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save sent news to a file
def save_sent_news(sent_news):
    with open('sent_news.json', 'w', encoding='utf-8') as file:
        json.dump(sent_news, file)

def main():
    sent_news = load_sent_news()
    news = fetch_news()
    
    # Filter new news
    new_news = [item for item in news if item['link'] not in sent_news]
    
    # Send new news via Telegram
    for item in new_news:
        message = f"Title: {item['title']}\nLink: {item['link']}"
        send_telegram_message(message)
        sent_news.append(item['link'])
    
    # Save updated sent news
    save_sent_news(sent_news)
    
    logging.info(f"Sent {len(new_news)} new news items.")
    
    # Sleep for 200 seconds
    time.sleep(200)

if __name__ == "__main__":
    while True:
        main()

import requests
from bs4 import BeautifulSoup
import logging
import json
import time
import os

TELEGRAM_TOKEN = os.getenv("API_TOKEN")

CHAT_ID = os.getenv("CHANNEL_ID")
# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

# Keywords to search for
keywords = "новости доллар"

# Load previously sent news
def load_sent_news(filename='sent_news.json'):
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Save sent news
def save_sent_news(sent_news, filename='sent_news.json'):
    with open(filename, 'w') as file:
        json.dump(sent_news, file)

# Function to send message to Telegram
def send_message_to_telegram(text):
    payload = {
        'chat_id': CHAT_ID,
        'text': text
    }
    response = requests.post(TELEGRAM_API_URL, data=payload)
    if response.ok:
        logging.info("Message sent successfully")
    else:
        logging.error("Failed to send message: %s", response.text)

# Function to scrape news
def scrape_news(url="https://www.google.ru/"):
    logging.info("Scraping news from %s", url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    # This will depend on the structure of the webpage you are scraping
    articles = []
    for item in soup.find_all('a'): # Adjust this based on the specific HTML element that contains news
        link = item.get('href')
        title = item.text
        if title and link:
            articles.append({'title': title, 'link': link})
    return articles

# Main function
def main():
    sent_news = load_sent_news()
    new_news = []

    while True:
        news = scrape_news()
        new_news = [item for item in news if item['link'] not in sent_news]

        for article in new_news:
            message = f"{article['title']}\n{article['link']}"
            send_message_to_telegram(message)
            sent_news.append(article['link'])  # Mark this article as sent

        save_sent_news(sent_news)
        time.sleep(200)  # Wait for 200 seconds before scraping again

if __name__ == "__main__":
    main()

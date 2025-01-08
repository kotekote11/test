import requests
from bs4 import BeautifulSoup
import logging
import time
import telegram  # Make sure you have python-telegram-bot installed: pip install python-telegram-bot
import os

TELEGRAM_BOT_TOKEN = os.getenv("API_TOKEN")

TELEGRAM_CHANNEL_ID = os.getenv("CHANNEL_ID")
# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


# Google Search URL
GOOGLE_SEARCH_URL = "https://www.google.ru/search?q={}&tbm=nws"
KEYWORDS = "новости евро"

# Telegram Channel URL to check for existing news
TELEGRAM_CHANNEL_URL = "https://t.me/s/fgtestfg"

def clean_url(url):
    """Extracts the actual URL from Google's redirect URL."""
    if url.startswith('/url?q='):
        url = url[len('/url?q='):]
    url = url.split('&sa=U&ved')[0]
    return url

def get_telegram_channel_links(channel_url):
    """Fetches existing news links from the Telegram channel."""
    try:
        response = requests.get(channel_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', class_='tgme_widget_message_link_preview')]
        return links
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Telegram channel: {e}")
        return []


def get_google_news(keywords):
    """Fetches news from Google based on keywords."""
    try:
        url = GOOGLE_SEARCH_URL.format(keywords)
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        news_items = []
        for h3_tag in soup.find_all('h3'):
            a_tag = h3_tag.find('a')
            if a_tag and 'href' in a_tag.attrs:
                news_url = clean_url(a_tag['href'])
                news_items.append({'title': h3_tag.text, 'url': news_url})
        return news_items
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching Google News: {e}")
        return []


def send_telegram_message(bot, message):
    """Sends a message to the Telegram channel."""
    try:
        bot.send_message(chat_id=TELEGRAM_CHANNEL_ID, text=message)
        logging.info(f"Sent message to Telegram: {message}")
    except Exception as e:
        logging.error(f"Error sending Telegram message: {e}")


def main():
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    while True:
        logging.info("Checking for new news...")
        try:
            google_news = get_google_news(KEYWORDS)
            if not google_news:
                logging.warning("No news found on Google.")
                continue

            telegram_links = get_telegram_channel_links(TELEGRAM_CHANNEL_URL)
            if telegram_links is None:
                logging.warning("Could not get links from telegram channel")
                continue

            for news_item in google_news:
                if news_item['url'] not in telegram_links:
                    message = f"<b>{news_item['title']}</b>\n\n{news_item['url']}"
                    send_telegram_message(bot, message)
                else:
                    logging.info(f"Skipping duplicate news: {news_item['url']}")

        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

        logging.info(f"Waiting {200} seconds before next check...")
        time.sleep(200)


if __name__ == "__main__":
    main()

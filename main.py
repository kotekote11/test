import os
import json
import logging
import aiohttp
import asyncio
from bs4 import BeautifulSoup
from aiogram import Bot
import random

# Load environment variables
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_LIST_FILE = 'dump.json'

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Keywords for search
KEYWORDS = [
    "открытие фонтанов 2025",
    "открытие фонтанов 2026",
    "открытие светомузыкального фонтана 2025"
]

# Ignore sets for filtering
IGNORE_WORDS = {"Петергоф", "нефть", "недр", "месторождение"}
IGNORE_SITES = {"instagram", "livejournal", "fontanka"}

# Function to load sent URLs
def load_sent_list():
    try:
        with open(SENT_LIST_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        return []
# Function to save sent URLs
def save_sent_list(sent_list):
    with open(SENT_LIST_FILE, 'w', encoding='utf-8') as file:
        json.dump(sent_list, file)
# Function to clean URLs
def clean_url(url):
    url = url[len('/url?q='):]
    return url.split('&sa=U&ved')[0]
# Function to search Google for articles
async def search_google(session, keyword):
    query = f'https://www.google.ru/search?q={keyword}&hl=ru&tbs=qdr:d'
    async with session.get(query) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        for item in soup.find_all('h3'):
            link = item.find('a')['href']
            cleaned_link = clean_url(link)
            articles.append(cleaned_link)
        return articles
# Function to search Yandex for articles
async def search_yandex(session, keyword):
    query = f'https://yandex.ru/search/?text={keyword}&within=77'
    async with session.get(query) as response:
        html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        articles = []
        for item in soup.find_all('a', href=True):
            cleaned_link = clean_url(item['href'])
            articles.append(cleaned_link)
        return articles
# Main monitoring function
async def monitor():
    sent_list = load_sent_list()
    bot = Bot(token=API_TOKEN)
    async with aiohttp.ClientSession() as session:
        while True:
            for keyword in KEYWORDS:
                logging.info("Checking keyword: %s", keyword)
                news_from_google = await search_google(session, keyword)
                news_from_yandex = await search_yandex(session, keyword)
                news = list(set(news_from_google + news_from_yandex))
                for link in news:
                    if link not in sent_list and not any(word in link for word in IGNORE_WORDS):
                        try:
                            title = link  # Replace with a function to fetch actual title
                            message_text = f"{title}\n{link}\n⛲@MonitoringFontan📰#Фонтан"
                            await bot.send_message(chat_id=CHANNEL_ID, text=message_text)
                            sent_list.append(link)
                            logging.info("Sent message: %s", message_text)
                            # Add random delay
                            await asyncio.sleep(random.randint(5, 15))
                        except Exception as e:
                            logging.error("Error sending message: %s", e)
                save_sent_list(sent_list)
            await asyncio.sleep(300)  # Wait for 5 minutes before the next check
if __name__ == "__main__":
    # Start monitoring
    loop = asyncio.get_event_loop()
    loop.run_until_complete(monitor())

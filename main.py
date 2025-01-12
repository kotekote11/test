import os
import json
import time
import asyncio
import logging
import requests
from bs4 import BeautifulSoup
import aiohttp
from typing import List, Set

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Environment variables
API_TOKEN = os.getenv("API_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
SENT_LIST_FILE = 'google.json'

# Keywords and filters
KEYWORDS = [
    "открытие фонтанов", 
    "открытие фонтанов 2025", 
    "открытие музыкального фонтана"
]
IGNORE_WORDS: Set[str] = {"нефть", "недр", "месторождение"}
IGNORE_SITES: Set[str] = {"instagram", "livejournal", "fontanka"}

def clean_url(url: str) -> str:
    """Clean and extract the original URL."""
    url = url[len('/url?q='):] if '/url?q=' in url else url
    url = url.split('&sa=U&ved')[0]
    return url

def load_sent_list() -> List[str]:
    """Load previously sent links."""
    try:
        with open(SENT_LIST_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_sent_list(sent_list: List[str]):
    """Save sent links to file."""
    with open(SENT_LIST_FILE, 'w') as file:
        json.dump(sent_list, file)

async def send_telegram_message(bot_token: str, chat_id: str, message: str):
    """Send message via Telegram Bot API."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data={
            'chat_id': chat_id,
            'text': message
        }) as response:
            return await response.json()

async def search_and_monitor(keyword: str):
    """Search and monitor results for a specific keyword."""
    sent_list = load_sent_list()
    repeat_count = 0

    while True:
        try:
            # Google search
            google_query = f'https://www.google.ru/search?q={keyword}&hl=ru&tbs=qdr:d'
            # Yandex search
            yandex_query = f'https://yandex.ru/search/?text={keyword}&within=77'

            # Perform searches (you'll need to implement actual search logic)
            # This is a placeholder for web scraping
            async with aiohttp.ClientSession() as session:
                for query in [google_query, yandex_query]:
                    async with session.get(query) as response:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        for result in soup.find_all('h3'):
                            link = result.find('a')['href']
                            title = result.text
                            
                            # URL cleaning and validation
                            cleaned_link = clean_url(link)
                            
                            # Skip if link already sent or contains ignore words/sites
                            if (cleaned_link in sent_list or 
                                any(word in title.lower() for word in IGNORE_WORDS) or
                                any(site in cleaned_link for site in IGNORE_SITES)):
                                continue
                            
                            # Validate link
                            try:
                                response = requests.head(cleaned_link)
                                if response.status_code != 200:
                                    continue
                            except Exception:
                                continue
                            
                            # Prepare message
                            message_text = f"{title}\n{cleaned_link}\n⛲@MonitoringFontan    📰#MonitoringFontan"
                            
                            # Send Telegram message
                            await send_telegram_message(API_TOKEN, CHANNEL_ID, message_text)
                            
                            # Update sent list
                            sent_list.append(cleaned_link)
                            
                            # Manage sent list size
                            if repeat_count % 90 == 0:
                                sent_list = sent_list[-9:]
                                save_sent_list(sent_list)
                            
                            repeat_count += 1

            # Wait before next iteration
            await asyncio.sleep(300)

        except Exception as e:
            logger.error(f"Error in search_and_monitor: {e}")
            await asyncio.sleep(300)

async def main():
    """Main async function to run keyword monitoring."""
    tasks = [search_and_monitor(keyword) for keyword in KEYWORDS]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())

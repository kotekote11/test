import logging
import json
import random
import time
import aiohttp
import feedparser
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
import os
BOT_TOKEN = os.getenv("API_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot token from @BotFather
#BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
HABR_RSS_URL = "https://habr.com/ru/rss/news/?fl=ru"

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Store previously sent articles to avoid duplicates
sent_articles = set()

async def fetch_habr_news():
    """Fetch and parse Habr RSS feed"""
    try:
        feed = feedparser.parse(HABR_RSS_URL)
        return feed.entries
    except Exception as e:
        logger.error(f"Error fetching RSS feed: {e}")
        return []

def format_article(article):
    """Format article data for sending"""
    return (f"📰 *{article.title}*\n\n"
            f"{article.description}\n\n"
            f"🔗 [Read more]({article.link})")

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """Handle /start command"""
    await message.reply(
        "👋 Welcome! I'm a Habr News Bot.\n"
        "Use /news to get a random article from Habr."
    )

@dp.message_handler(commands=['news'])
async def send_random_news(message: types.Message):
    """Handle /news command"""
    try:
        articles = await fetch_habr_news()
        if not articles:
            await message.reply("Sorry, couldn't fetch news at the moment.")
            return

        # Filter out previously sent articles
        available_articles = [a for a in articles if a.link not in sent_articles]
        
        if not available_articles:
            sent_articles.clear()  # Reset if all articles have been sent
            available_articles = articles

        article = random.choice(available_articles)
        sent_articles.add(article.link)

        await message.reply(
            format_article(article),
            parse_mode=types.ParseMode.MARKDOWN,
            disable_web_page_preview=False
        )

    except Exception as e:
        logger.error(f"Error sending news: {e}")
        await message.reply("Sorry, an error occurred while processing your request.")

async def scheduled_news():
    """Function to send periodic updates"""
    while True:
        try:
            articles = await fetch_habr_news()
            if articles:
                article = random.choice(articles)
                # Replace CHANNEL_ID with your channel's ID
                await bot.send_message(
                    chat_id="CHANNEL_ID",
                    text=format_article(article),
                    parse_mode=types.ParseMode.MARKDOWN,
                    disable_web_page_preview=False
                )
        except Exception as e:
            logger.error(f"Error in scheduled news: {e}")
        
        await asyncio.sleep(200)  # Wait for 200 seconds

if __name__ == '__main__':
    from aiogram import executor
    import asyncio
    
    # Start scheduled task
    loop = asyncio.get_event_loop()
    loop.create_task(scheduled_news())
    
    # Start polling
    executor.start_polling(dp, skip_updates=True)

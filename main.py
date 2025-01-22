import logging
import time
from news_from_google import get_news_from_google
from news_from_yandex import get_news_from_yandex

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def run_news_fetcher(function, keyword):
    logger.info(f"Запуск {function.__name__}...")
    news = function(keyword)
    for title, link in news:
        logger.info(f"{title}: {link}")

while True:
    keyword = "новости"
    run_news_fetcher(get_news_from_google, keyword)
    run_news_fetcher(get_news_from_yandex, keyword)
    
    logger.info("Ожидание перед следующим циклом...")
    time.sleep(1300)

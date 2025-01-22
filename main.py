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

# Ключевые слова для поиска
KEYWORDS = [
    "открытие фонтанов 2025",
    "открытие фонтанов 2026",
    "открытие светомузыкального фонтана 2025",
]

# Обязательные и игнорируемые слова
MUST_HAVE_WORDS = {"фонтан", "фонтанов", "фонтана"}
IGNORE_WORDS = {"Петергоф", "нефть", "недр", "месторождение"}
IGNORE_SITES = {"instagram", "livejournal", "fontanka", "avito"}

def run_news_fetcher(function, keyword):
    logger.info(f"Запуск {function.__name__}...")
    news = function(keyword)
    for title, link in news:
        if all(word not in title.lower() for word in IGNORE_WORDS) \
           and not any(site in link for site in IGNORE_SITES) \
           and any(word in title.lower() for word in MUST_HAVE_WORDS):
            logger.info(f"{title}: {link}")

while True:
    for keyword in KEYWORDS:
        run_news_fetcher(get_news_from_google, keyword)
        run_news_fetcher(get_news_from_yandex, keyword)
    
    logger.info("Ожидание перед следующим циклом...")
    time.sleep(1300)
    

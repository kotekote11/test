import logging
import subprocess
import time

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s]: %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

while True:
    logger.info("Запуск news_from_google.py...")
    subprocess.run(["python", "news_from_google.py"], capture_output=True)
    
    logger.info("Запуск news_from_yandex.py...")
    subprocess.run(["python", "news_from_yandex.py"], capture_output=True)
    
    logger.info("Ожидание перед следующим циклом...")
    time.sleep(1300)

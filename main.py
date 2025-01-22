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

# Определите период ожидания в секундах
WAIT_TIME = 1300  # 22 минуты

try:
    while True:
        # Запуск news_from_google.py
        logger.info("Запуск news_from_google.py...")
        try:
            result = subprocess.run(
                ["python", "news_from_google.py"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Вывод news_from_google.py: %s", result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error("Ошибка при выполнении news_from_google.py: %s", e.stderr)

        # Запуск news_from_yandex.py
        logger.info("Запуск news_from_yandex.py...")
        try:
            result = subprocess.run(
                ["python", "news_from_yandex.py"],
                capture_output=True,
                text=True,
                check=True
            )
            logger.info("Вывод news_from_yandex.py: %s", result.stdout)
        except subprocess.CalledProcessError as e:
            logger.error("Ошибка при выполнении news_from_yandex.py: %s", e.stderr)

        # Ожидание перед следующим циклом
        logger.info("Ожидание перед следующим циклом на %d секунд...", WAIT_TIME)
        time.sleep(WAIT_TIME)

except KeyboardInterrupt:
    logger.info("Цикл остановлен пользователем.")
except Exception as e:
    logger.error("Произошла ошибка: %s", str(e))

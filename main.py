import logging
import subprocess
import time
from subprocess import CalledProcessError, TimeoutExpired, OSError

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
                timeout=60  # Установите допустимое время ожидания
            )
            logger.info("Вывод news_from_google.py: %s", result.stdout)
            logger.info("Код завершения news_from_google.py: %d", result.returncode)
        except CalledProcessError as e:
            logger.error("Ошибка при выполнении news_from_google.py: %s", e.stderr)
        except TimeoutExpired:
            logger.error("Превышено время ожидания для news_from_google.py")
        except OSError as e:
            logger.error("Ошибка ОС при выполнении news_from_google.py: %s", str(e))

        # Запуск news_from_yandex.py
        logger.info("Запуск news_from_yandex.py...")
        try:
            result = subprocess.run(
                ["python", "news_from_yandex.py"],
                capture_output=True,
                text=True,
                timeout=60  # Установите допустимое время ожидания
            )
            logger.info("Вывод news_from_yandex.py: %s", result.stdout)
            logger.info("Код завершения news_from_yandex.py: %d", result.returncode)
        except CalledProcessError as e:
            logger.error("Ошибка при выполнении news_from_yandex.py: %s", e.stderr)
        except TimeoutExpired:
            logger.error("Превышено время ожидания для news_from_yandex.py")
        except OSError as e:
            logger.error("Ошибка ОС при выполнении news_from_yandex.py: %s", str(e))

        # Ожидание перед следующим циклом
        logger.info("Ожидание перед следующим циклом на %d секунд...", WAIT_TIME)
        time.sleep(WAIT_TIME)

except KeyboardInterrupt:
    logger.info("Цикл остановлен пользователем.")
except Exception as e:
    logger.error("Произошла ошибка: %s", str(e))
finally:
    logger.info("Завершение работы программы.")

import concurrent.futures
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

def run_script(script_name):
    logger.info(f"Запуск {script_name}...")
    subprocess.run([f"python {script_name}"], capture_output=True)

while True:
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(run_script, "news_from_google.py"): "Google",
            executor.submit(run_script, "news_from_yandex.py"): "Yandex"
        }

        for future in concurrent.futures.as_completed(futures):
            service = futures[future]
            try:
                future.result()
            except Exception as exc:
                logger.exception(f"Ошибка при выполнении {service}: {exc}")

    logger.info("Ожидание перед следующим циклом...")
    time.sleep(1300)
    

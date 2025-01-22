import subprocess
import time
import logging

# Уровень логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_script(script_name):
    try:
        logging.info(f'Запуск скрипта: {script_name}')
        # Запускаем скрипт в фоновом режиме
        process = subprocess.Popen(["python", script_name])
        return process
    except Exception as e:
        logging.error(f'Ошибка при запуске {script_name}: {e}')
        return None

while True:
    google_process = run_script("news_from_google.py")
    yandex_process = run_script("news_from_yandex.py")

    # Дождаться завершения обоих процессов
    if google_process:
        google_process.wait()  # Дожидаемся завершения
        logging.info(f'Скрипт news_from_google.py завершился с кодом: {google_process.returncode}')

    if yandex_process:
        yandex_process.wait()  # Дожидаемся завершения
        logging.info(f'Скрипт news_from_yandex.py завершился с кодом: {yandex_process.returncode}')

    logging.info('Ожидание перед следующей итерацией...')
    time.sleep(1300)  # Пауза перед следующей итерацией

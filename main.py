import subprocess
import time
import logging

# Уровень логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_script(script_name):
    try:
        logging.info(f'Запуск скрипта: {script_name}')
        result = subprocess.run(["python", script_name], check=True)
        logging.info(f'Скрипт {script_name} завершился с кодом: {result.returncode}')
    except subprocess.CalledProcessError as e:
        logging.error(f'Ошибка при выполнении {script_name}: {e}')

while True:
    run_script("news_from_yandex.py")
    run_script("news_from_google.py")
    
    logging.info('Ожидание перед следующей итерацией...')
    time.sleep(1300)  # Пауза перед следующей итерацией

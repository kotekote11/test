import subprocess
import time
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Maximum number of restart attempts
MAX_RESTART_ATTEMPTS = 3

def run_script(script_name, restart_count=0):
    try:
        logging.info(f'Запуск скрипта: {script_name}')
        process = subprocess.Popen(["python", script_name])
        return process
    except Exception as e:
        logging.error(f'Ошибка при запуске {script_name}: {e}')
        return None

def monitor_process(script_name, process, restart_count=0):
    try:
        process.wait()
        
        # Check if process exited unexpectedly
        if process.returncode != 0:
            logging.warning(f'Скрипт {script_name} завершился с кодом ошибки: {process.returncode}')
            
            # Restart script if max attempts not reached
            if restart_count < MAX_RESTART_ATTEMPTS:
                logging.info(f'Попытка перезапуска {script_name} (Попытка {restart_count + 1})')
                new_process = run_script(script_name, restart_count + 1)
                
                if new_process:
                    monitor_process(script_name, new_process, restart_count + 1)
            else:
                logging.error(f'Превышено максимальное количество попыток перезапуска для {script_name}')
        else:
            logging.info(f'Скрипт {script_name} завершился успешно с кодом: {process.returncode}')
    
    except Exception as e:
        logging.error(f'Ошибка при мониторинге {script_name}: {e}')

def main():
    try:
        while True:
            # Run scripts
            google_process = run_script("news_from_google.py")
            yandex_process = run_script("news_from_yandex.py")

            # Monitor processes
            if google_process:
                monitor_process("news_from_google.py", google_process)
            
            if yandex_process:
                monitor_process("news_from_yandex.py", yandex_process)

            logging.info('Ожидание перед следующей итерацией...')
            time.sleep(1300)

    except KeyboardInterrupt:
        logging.info('Программа остановлена пользователем')
        sys.exit(0)
    except Exception as e:
        logging.error(f'Непредвиденная ошибка: {e}')
        sys.exit(1)

if __name__ == "__main__":
    main()

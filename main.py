import subprocess
import time

while True:
    print("Запуск news_from_google.py...")
    subprocess.run(["python", "news_from_google.py"])
    
    print("Запуск news_from_yandex.py...")
    subprocess.run(["python", "news_from_yandex.py"])
    
    print("Ожидание перед следующим циклом...")
    time.sleep(1300)

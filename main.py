import subprocess
import time
while True:
   subprocess.run(["python", "news_from_google.py"])
   subprocess.run(["python", "news_from_yandex.py"])
   time.sleep(1300)

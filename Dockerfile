FROM python:3.12
WORKDIR /app
COPY . /app
RUN pip install requests
RUN pip install beautifulsoup4
RUN pip install python-telegram-bot
RUN pip install --upgrade python-telegram-bot
CMD ["python", "main.py"]

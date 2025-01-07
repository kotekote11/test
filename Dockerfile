FROM python:3.12
WORKDIR /app
COPY . /app
RUN pip install requests
RUN pip install aiogram feedparser aiohttp
CMD ["python", "main.py"]

import asyncio
import json
import logging
import os
import random
import time
from bs4 import BeautifulSoup
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

telegram_api_key = os.getenv("API_TOKEN")

#CHANNEL_ID = os.getenv("CHANNEL_ID")
# Включить уровень логирования DEBUG
logging.basicConfig(level=logging.DEBUG)

# Создать бота
with open('settings.json') as f:
    settings = json.loads(f.read())
bot = Bot(token=settings['telegram_api_key'])
dp = Dispatcher(bot)

# Список отправленных новостей
sent_news = []

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я буду присылать тебе новости по заданному запросу.")
    await message.answer("Введи поисковый запрос:")

# Обработчик текстовых сообщений
@dp.message_handler()
async def text_message_handler(message: types.Message):
    # Получить поисковый запрос
    query = message.text

    # Получить новости по запросу
    news = get_news(query)

    # Отфильтровать новые новости
    new_news = [item for item in news if item['link'] not in sent_news]

    # Отправить новые новости пользователю
    for item in new_news:
        await bot.send_message(message.chat.id, f"{item['title']}\n{item['link']}")

    # Обновить список отправленных новостей
    sent_news.extend([item['link'] for item in new_news])

    # Сохранить список отправленных новостей в файл
    with open('sent_news.json', 'w') as file:
        json.dump(sent_news, file)

# Функция для получения новостей по запросу
def get_news(query):
    # Сформировать URL-адрес запроса
    url = f"https://www.google.ru/search?q={query}"

    # Отправить запрос и получить ответ
    response = requests.get(url)

    # Проверить код ответа
    if response.status_code != 200:
        raise Exception("Ошибка при получении новости")

    # Распарсить HTML-ответ
    soup = BeautifulSoup(response.text, 'html.parser')

    # Найти результаты поиска
    results = soup.find_all('div', class_='g')

    # Извлечь заголовки и ссылки на новости
    news = []
    for result in results:
        title = result.find('h3').text
        link = result.find('a')['href']
        news.append({'title': title, 'link': link})

    # Вернуть список новостей
    return news

# Загрузить список отправленных новостей из файла
if os.path.isfile('sent_news.json'):
    with open('sent_news.json') as file:
        sent_news = json.load(file)

# Запустить цикл обработки сообщений
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

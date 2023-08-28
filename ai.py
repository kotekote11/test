import time

import feedparser
import telebot

# Получите токен бота у @BotFather в Telegram
bot_token = '6483504124:AAFnG1QAy6hamm5QRtkEQQgVGw24aLSZGgs'

# Создайте объект Telegram Bot
#bot = telegram.Bot(token=bot_token)
bot = telebot.TeleBot(token=bot_token)
# Получите chat_id вашего телеграм-канала, в который хотите отправлять новости
channel_chat_id = '@svodki_digest'

# Получите URL RSS-ленты с новостями
rss_feed_url = 'https://habr.com/ru/rss/flows/admin/news/?fl=ru'

# Список запросов для фильтрации новостей
search_queries = ['cloud', 'beeline']

def send_news_to_channel(item):
    # Извлеките заголовок и ссылку на новость из элемента RSS-ленты
    news_title = item['description']
    news_link = item['title']
    
    # Отправьте новость в телеграм-канал
    bot.send_message(chat_id=channel_chat_id, text=f'{news_title}\n{news_link}')

def process_news_feed():
    try:
        # Загрузите RSS-ленту
        feed = feedparser.parse(rss_feed_url)
        
        # Проверьте, была ли лента успешно загружена
        if feed.bozo == 0:
            # Пройдитесь по каждой новости в ленте
            for item in feed.entries:
                # Проверьте каждую новость на наличие ключевых слов
                for query in search_queries:
                    if query.lower() in item.title.lower():
                        # Отправьте новость в телеграм-канал
                        send_news_to_channel(item)
                        break
            
            print('News sent successfully.')
            
        else:
            print('Failed to load RSS feed.')
            
    except Exception as e:
        print('Exception:', e)

# Бесконечный цикл для проверки новостей каждые 5 минут
while True:
    process_news_feed()
    # Подождите 5 минут перед повторной проверкой
    time.sleep(300)

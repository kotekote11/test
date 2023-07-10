import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, MessageFilters

# Устанавливаем уровень логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Инициализируем Updater и передаем ему токен вашего бота
updater = Updater(token='5700959339:AAEXSEfnjDg6zrl7bLUN1W_ISJtF6FiKd_0', use_context=True)
dispatcher = updater.dispatcher

# Обработчик команды /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет! Я бот.")

# Регистрируем обработчик команды /start
start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

# Обработчик текстовых сообщений
def echo(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)

# Регистрируем обработчик текстовых сообщений
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
dispatcher.add_handler(echo_handler)

# Запускаем бота
updater.start_polling()

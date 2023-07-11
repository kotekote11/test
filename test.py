#from telegram import Update
#from telegram.ext import CommandHandler, MessageHandler, ContextTypes, Application, filters
import random


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    await update.message.reply_text('Привет! Я бот для раздачи бонусов.')


async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /bonus."""
    bonus_amount = random.randint(1, 100)  # Генерация случайного бонуса
    await update.message.reply_text(f'Ваш бонус: {bonus_amount}')

bonus
async def statistics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /statistics."""
    await update.message.reply_text('Здесь будет статистика.')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик сообщений."""
    text = update.message.text.lower()
    if text == 'бонус':
        await bonus(update, context)
    elif text == 'статистика':
        await statistics(update, context)


def main():
    # Инициализация бота
#    application = Application.builder().token("5818778889:AAGNDQOGIJBr4o7TVPZvFXNqFhD8egSd0Oo").build()

    # Обработчики команд
    application.add_handlers([
        CommandHandler("start", start),
        CommandHandler("bonus", bonus),
        CommandHandler("statistics", statistics)
    ])

    # Обработчик сообщений
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()
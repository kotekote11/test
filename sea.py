python
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Функция для обработки команды /start
def start_command(update: Update, context: CallbackContext) -> None:
    # Отправляем сообщение с приветствием пользователю
    update.message.reply_text('Привет!')

# Функция для обработки текстовых сообщений
def text_message(update: Update, context: CallbackContext) -> None:
    # Получаем текст сообщения, отправленного пользователем
    message_text = update.message.text
    # Отправляем пользователю его же сообщение в ответ
    update.message.reply_text(message_text)

def main() -> None:
    # Создаем экземпляр класса Updater и передаем ему токен вашего бота
    updater = Updater('5700959339:AAEXSEfnjDg6zrl7bLUN1W_ISJtF6FiKd_0')

    # Получаем объект диспетчера для регистрации обработчиков
    dispatcher = updater.dispatcher

    # Регистрируем обработчик команды /start с функцией start_command
    dispatcher.add_handler(CommandHandler('start', start_command))

    # Регистрируем обработчик для текстовых сообщений с функцией text_message
    dispatcher.add_handler(MessageHandler(Filters.text, text_message))

    # Запускаем бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

from telegram.ext import Updater, CommandHandler, MessageHandler

updater = Updater(token='5700959339:AAEXSEfnjDg6zrl7bLUN1W_ISJtF6FiKd_0', use_context=True)
dispatcher = updater.dispatcher

def handle_message(update, context):
    text = update.message.text
    if text == '/start':
        context.bot.send_message(chat_id=update.effective_chat.id, text='Hello!')
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Received: ' + text)

message_handler = MessageHandler(Filters.text, handle_message)
dispatcher.add_handler(message_handler)

updater.start_polling()

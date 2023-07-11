#from telegram.ext import Updater, MessageHandler, Filters
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext, Application, filters
import openai

openai.api_key = "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"
TELEGRAM_API_TOKEN = "6074730982:AAGKU2_gpogdkTQvmE4Ya63n9ot2dHVzA7I"

async def text_message(update, context):
    response = openai.Completion.create(
        engine="davinci",
        prompt="Hello, world!",
        max_tokens=5
    )
    await update.message.reply_text(response.choices[0].text)

def main():
    application = Application.builder().token("5818778889:AAGNDQOGIJBr4o7TVPZvFXNqFhD8egSd0Oo").build()

#updater = Updater(TELEGRAM_API_TOKEN, use_context=True)
#dispatcher = updater.dispatcher
application.add_handler(MessageHandler(filters.text & (filters.command), text_message))
   # Запуск бота
#application.run_polling()

updater.start_polling()
updater.idle()

if __name__ == '__main__':
    main()
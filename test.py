from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, ContextTypes, Application, filters
#from telegram.ext import Updater, MessageHandler
import openai

openai.api_key = "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"
TELEGRAM_API_TOKEN = "5818778889:AAGNDQOGIJBr4o7TVPZvFXNqFhD8egSd0Oo"

def text_message(update, context):
    response = openai.Completion.create(
        engine="davinci",
        prompt="Hello, world!",
        max_tokens=5
    )
    update.message.reply_text(response.choices[0].text)

application = Application.builder().token("5818778889:AAGNDQOGIJBr4o7TVPZvFXNqFhD8egSd0Oo").build()
#updater = Updater("5818778889:AAGNDQOGIJBr4o7TVPZvFXNqFhD8egSd0Oo")
#dispatcher = updater.dispatcher
#application.add_handler(MessageHandler(Filters.text & (Filters.command), text_message))
#updater.start_polling()
#updater.idle()
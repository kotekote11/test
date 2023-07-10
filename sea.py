import telebot

bot = telebot.TeleBot('5700959339:AAEXSEfnjDg6zrl7bLUN1W_ISJtF6FiKd_0')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Привет, я бот! Как я могу тебе помочь?")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.polling()
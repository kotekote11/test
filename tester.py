application = Application.builder().token("здесь ваш токен").build()

# Регистрация обработчика на текстовые сообщения, но не команды
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# Запуск бота
application.run_polling()
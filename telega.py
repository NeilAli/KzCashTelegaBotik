import telebot

# Замените 'YOUR_TELEGRAM_BOT_TOKEN' на токен вашего бота
bot = telebot.TeleBot('6606877213:AAHepTun9NsQuZIhTLF8D12hdEcvfddc7vg')

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)

bot.polling()

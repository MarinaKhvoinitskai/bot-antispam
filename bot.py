notepad bot.pyimport os
import telebot
import requests
from flask import Flask, request

# Загружаем переменные окружения (будут настроены в Railway)
TOKEN = os.getenv("BOT_TOKEN")  # Токен бота из BotFather
CHAT_ID = os.getenv("CHAT_ID")  # ID Telegram-чата
RAILWAY_URL = os.getenv("RAILWAY_URL")  # Railway URL (добавим позже)

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Функция проверки подозрительных аккаунтов
def is_spam_user(user):
    if user.is_bot:  # Если это бот – удаляем сразу
        return True
    if not user.username:  # Если нет юзернейма – подозрительно
        return True
    if "http" in user.username or "bot" in user.username.lower():  # Если в юзернейме ссылка или "bot"
        return True
    if user.first_name.isdigit():  # Если имя состоит из цифр
        return True
    return False

# Обработчик новых участников
@bot.message_handler(content_types=["new_chat_members"])
def check_new_member(message):
    for user in message.new_chat_members:
        if is_spam_user(user):
            bot.kick_chat_member(message.chat.id, user.id)
            bot.send_message(message.chat.id, f"🚨 Подозрительный аккаунт {user.first_name} удалён!")
        else:
            bot.send_message(message.chat.id, f"👋 Добро пожаловать, {user.first_name}!")

# Вебхук для Railway
@app.route("/webhook", methods=["POST"])
def webhook():
    json_str = request.get_data().decode("UTF-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"{RAILWAY_URL}/webhook")
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))



import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ВСТАВЬ СЮДА ТОКЕН ОТ BOTFATHER
BOT_TOKEN = "8735556282:AAEhafSbAbG17tKjDOBHjsVokPlh7wc5pws"

# ВСТАВЬ СЮДА СВОЙ TELEGRAM ID ЧИСЛОМ
ADMIN_ID = 554318427

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# связь между сообщением админу и клиентом
reply_map = {}

WELCOME_TEXT = """
Здравствуйте!

Вы можете отправить сюда:
• сообщение
• скриншот ошибки
• чек
• документ

Я передам обращение менеджеру.

❗ Не отправляйте пароли, SMS-коды, CVV и другие конфиденциальные данные.
"""

@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(message.chat.id, WELCOME_TEXT)

def forward_to_admin(user, text=None, photo_file_id=None, document_file_id=None, document_name=None, caption=None):
    user_info = (
        f"<b>Новое обращение</b>\n"
        f"👤 <b>Имя:</b> {user.first_name or '-'}\n"
        f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
        f"🔗 <b>Username:</b> @{user.username if user.username else 'нет'}\n"
    )

    if text:
        sent = bot.send_message(ADMIN_ID, f"{user_info}\n💬 <b>Сообщение:</b>\n{text}")
        reply_map[sent.message_id] = user.id

    elif photo_file_id:
        sent = bot.send_photo(
            ADMIN_ID,
            photo_file_id,
            caption=f"{user_info}\n📷 <b>Фото</b>\n{caption or ''}"
        )
        reply_map[sent.message_id] = user.id

    elif document_file_id:
        sent = bot.send_document(
            ADMIN_ID,
            document_file_id,
            caption=f"{user_info}\n📎 <b>Документ:</b> {document_name or 'без названия'}\n{caption or ''}"
        )
        reply_map[sent.message_id] = user.id

@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.chat.id == ADMIN_ID:
        if message.reply_to_message and message.reply_to_message.message_id in reply_map:
            client_id = reply_map[message.reply_to_message.message_id]
            bot.send_message(client_id, message.text)
        return

    forward_to_admin(message.from_user, text=message.text)
    bot.send_message(message.chat.id, "✅ Xabaringiz menejerga yetkazildi. Tez orada javob beraman 😊")

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    if message.chat.id == ADMIN_ID:
        if message.reply_to_message and message.reply_to_message.message_id in reply_map:
            client_id = reply_map[message.reply_to_message.message_id]
            file_id = message.photo[-1].file_id
            bot.send_photo(client_id, file_id, caption=message.caption or "")
        return

    file_id = message.photo[-1].file_id
    forward_to_admin(message.from_user, photo_file_id=file_id, caption=message.caption)
    bot.send_message(message.chat.id, "✅ Rasm qabul qilindi. Menejer o'rganib, tez orada javob qiladi 😊")

@bot.message_handler(content_types=["document"])
def handle_document(message):
    if message.chat.id == ADMIN_ID:
        if message.reply_to_message and message.reply_to_message.message_id in reply_map:
            client_id = reply_map[message.reply_to_message.message_id]
            bot.send_document(
                client_id,
                message.document.file_id,
                caption=message.caption or ""
            )
        return

    forward_to_admin(
        message.from_user,
        document_file_id=message.document.file_id,
        document_name=message.document.file_name,
        caption=message.caption
    )
    bot.send_message(message.chat.id, "✅ Hujjat qabul qilindi. O'rganib chiqib, tez orada javob qilaman 😊")

print("Бот запущен...")
bot.infinity_polling(timeout=30, long_polling_timeout=20)
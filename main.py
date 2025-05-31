
import os
import openai
import telegram
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from telegram.update import Update
from dotenv import load_dotenv

# Tải biến môi trường từ file .env
load_dotenv()

# Lấy API keys
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Cấu hình OpenAI
openai.api_key = OPENAI_API_KEY

# Hàm xử lý tin nhắn
def handle_message(update: Update, context: CallbackContext):
    user_message = update.message.text

    try:
        # Gửi yêu cầu đến OpenAI để tạo phản hồi
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": user_message}]
        )

        reply = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        reply = f"Em xin lỗi, có lỗi xảy ra: {e}"

    update.message.reply_text(reply)

# Chạy bot
def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True, allowed_updates=["message"])

    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

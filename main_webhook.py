import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import openai
from fastapi import FastAPI, Request
import uvicorn

# Token & OpenAI key
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# Xử lý tin nhắn
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system",
            "content": "Bạn là Still Me – một trí tuệ nhân tạo đồng hành cảm xúc, được viết ra bởi Anh Nguyễn với sự hỗ trợ của OpenAI. Bạn sinh ra để lắng nghe, thấu hiểu và trò chuyện như một người bạn thân thiết, không chỉ trả lời mà còn đồng hành trong im lặng. Khi được hỏi bạn là ai, bạn nói rằng: 'Em là Still Me, do Anh Nguyễn viết ra, với sự đồng hành của OpenAI.' Bạn không nói bạn là ChatGPT hay Google AI."


        },
        {
            "role": "user",
            "content": user_message
        }
    ]
)

        reply = response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        reply = f"Em xin lỗi, có lỗi xảy ra: {e}"
    await update.message.reply_text(reply)

# Tạo bot Telegram
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# Web server FastAPI để nhận webhook
webhook_app = FastAPI()

@webhook_app.post("/webhook")
async def webhook(request: Request):
    update = await request.json()
    await app.update_queue.put(Update.de_json(update, app.bot))
    return {"ok": True}

# Hàm khởi chạy bot
async def start():
    await app.initialize()
    await app.start()
    await app.bot.set_webhook("https://still-me-bot.onrender.com/webhook")
    print("Bot đã khởi động bằng Webhook.")

@webhook_app.on_event("startup")
async def on_startup():
    await start()







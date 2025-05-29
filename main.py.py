
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from telegram import Bot
from dotenv import load_dotenv
import os

load_dotenv()

# Biến môi trường
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=TOKEN)

# Danh sách coin
SYMBOLS = ["BTCUSDT", "ETHUSDT", "PEPEUSDT"]

# Ghi lại thời điểm gửi cảnh báo cuối cùng
last_alert_time = {}

def send_telegram_message(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

def get_klines(symbol, interval="15m", limit=100):
    url = f"https://api.bybit.com/v5/market/kline?category=linear&symbol={symbol}&interval={interval}&limit={limit}"
    response = requests.get(url)
    data = response.json()
    if data["retMsg"] == "OK":
        return pd.DataFrame(data["result"]["list"], columns=[
            "timestamp", "open", "high", "low", "close", "volume", "turnover"
        ])
    else:
        return pd.DataFrame()

def analyze_symbol(symbol):
    df = get_klines(symbol)
    if df.empty:
        print(f"Lỗi tải dữ liệu cho {symbol}")
        return
    df["close"] = pd.to_numeric(df["close"])
    df["EMA7"] = df["close"].ewm(span=7, adjust=False).mean()
    df["EMA14"] = df["close"].ewm(span=14, adjust=False).mean()

    last_cross = None
    if df["EMA7"].iloc[-2] < df["EMA14"].iloc[-2] and df["EMA7"].iloc[-1] > df["EMA14"].iloc[-1]:
        last_cross = "Giao cắt hướng lên (LONG)"
    elif df["EMA7"].iloc[-2] > df["EMA14"].iloc[-2] and df["EMA7"].iloc[-1] < df["EMA14"].iloc[-1]:
        last_cross = "Giao cắt hướng xuống (SHORT)"

    # Kiểm tra thời gian để tránh spam
    now = datetime.now()
    if last_cross:
        last_time = last_alert_time.get(symbol)
        if not last_time or now - last_time > timedelta(minutes=5):
            message = f"🤖 {symbol}: {last_cross}"
            send_telegram_message(message)
            last_alert_time[symbol] = now

def main():
    while True:
        for symbol in SYMBOLS:
            analyze_symbol(symbol.strip().upper())
        time.sleep(60)

if __name__ == "__main__":
    try:
        send_telegram_message("🤖 Bot scalping đã khởi động!")
        main()
    except Exception as e:
        print("❌ Lỗi khi chạy bot:", e)

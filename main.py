import os
import time
import requests
from ta.trend import EMAIndicator
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BYBIT_API_KEY")
API_SECRET = os.getenv("BYBIT_API_SECRET")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SYMBOLS = os.getenv("SYMBOLS", "PEPEUSDT").split(",")

def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except:
        print("Lỗi gửi tin nhắn Telegram")

def fetch_ohlcv(symbol):
    url = f"https://api.bybit.com/v5/market/kline"
    params = {
        "category": "linear",
        "symbol": symbol,
        "interval": "15",
        "limit": 100
    }
    try:
        res = requests.get(url, params=params).json()
        if res["retCode"] == 0:
            df = pd.DataFrame(res["result"]["list"],
                              columns=["timestamp", "open", "high", "low", "close", "volume", "_", "__"])
            df["close"] = pd.to_numeric(df["close"])
            return df
    except:
        return None

def analyze_symbol(symbol):
    df = fetch_ohlcv(symbol)
    if df is None or df.empty:
        return

    ema7 = EMAIndicator(close=df["close"], window=7).ema_indicator()
    ema21 = EMAIndicator(close=df["close"], window=21).ema_indicator()

    last_cross = None
    if ema7.iloc[-2] < ema21.iloc[-2] and ema7.iloc[-1] > ema21.iloc[-1]:
        last_cross = "LONG"
    elif ema7.iloc[-2] > ema21.iloc[-2] and ema7.iloc[-1] < ema21.iloc[-1]:
        last_cross = "SHORT"

    if last_cross:
        send_telegram_message(f"Tín hiệu {last_cross} {symbol} tại giá {df['close'].iloc[-1]}")

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

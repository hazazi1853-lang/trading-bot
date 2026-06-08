from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

TELEGRAM_TOKEN = "8960308840:AAE8ygz4cQZJSLjDokfRNn_XDRAz-D5nJTY"
CHAT_ID = "740129456"

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "no data"}), 400
    signal = data.get("signal", "")
    symbol = data.get("symbol", "XAUUSD")
    price = float(data.get("price", 0))
    timeframe = data.get("timeframe", "5M")
    if signal == "buy":
        sl = round(price - (price * 0.001), 2)
        tp1 = round(price + (price * 0.002), 2)
        tp2 = round(price + (price * 0.004), 2)
        emoji = "🟢"
        action = "شراء"
    elif signal == "sell":
        sl = round(price + (price * 0.001), 2)
        tp1 = round(price - (price * 0.002), 2)
        tp2 = round(price - (price * 0.004), 2)
        emoji = "🔴"
        action = "بيع"
    else:
        return jsonify({"error": "unknown signal"}), 400
    message = f"{emoji} <b>إشارة {action}</b>\n\n📊 <b>الزوج:</b> {symbol}\n⏱ <b>التايم فريم:</b> {timeframe}\n💰 <b>الدخول:</b> {price}\n🛑 <b>وقف الخسارة:</b> {sl}\n🎯 <b>الهدف 1:</b> {tp1}\n🎯 <b>الهدف 2:</b> {tp2}\n\n⚠️ إدارة رأس المال أولاً"
    send_telegram(message)
    return jsonify({"status": "ok"})

@app.route("/", methods=["GET"])
def home():
    return "السيرفر يعمل!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

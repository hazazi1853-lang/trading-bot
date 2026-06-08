import os
import requests
import base64
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = "8960308840:AAE8ygz4cQZJSLjDokfRNn_XDRAz-D5nJTY"
CHAT_ID = "740129456"
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "")

def analyze_chart(image_base64):
    headers = {"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    body = {"model": "claude-opus-4-6", "max_tokens": 1024, "messages": [{"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_base64}}, {"type": "text", "text": "أنت محلل تداول خبير. حلل هذا الشارت وأعطني:\n📊 الاتجاه: [صعود/هبوط/جانبي]\n🎯 الإشارة: [شراء/بيع/انتظار]\n💰 الدخول: [السعر]\n🛑 وقف الخسارة: [السعر]\n🎯 الهدف 1: [السعر]\n🎯 الهدف 2: [السعر]\n✅ الثقة: [النسبة]%\n📝 ملاحظة: [جملة واحدة]"}]}]}
    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body)
    return response.json()["content"][0]["text"]

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    data = request.json
    if not data:
        return {"ok": True}
    message = data.get("message", {})
    photo = message.get("photo")
    chat_id = message.get("chat", {}).get("id")
    if photo:
        file_id = photo[-1]["file_id"]
        file_path = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}").json()["result"]["file_path"]
        img = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}").content
        img_base64 = base64.b64encode(img).decode("utf-8")
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": "⏳ جاري تحليل الشارت..."})
        analysis = analyze_chart(img_base64)
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": analysis})
    elif message.get("text") == "/start":
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": "👋 أهلاً! أرسل لي صورة الشارت وأحللها فوراً 📊"})
    return {"ok": True}

@app.route("/", methods=["GET"])
def home():
    return "البوت يعمل!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

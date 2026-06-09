import os
import requests
import base64
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_TOKEN = "8960308840:AAE8ygz4cQZJSLjDokfRN"
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")

processed_updates = set()

def send_message(chat_id, text):
    requests.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
        json={"chat_id": chat_id, "text": text})

def analyze_chart(image_base64):
    headers = {
        "x-api-key": ANTHROPIC_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    body = {
        "model": "claude-haiku-4-5-20251001",
        "max_tokens": 1024,
        "messages": [{
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": image_base64}},
                {"type": "text", "text": "حلل هذا الشارت وأعطني:\n📊 الاتجاه: [صعود/هبوط/جانبي]\n🎯 الإشارة: [شراء/بيع/انتظار]\n💰 الدخول: [السعر]\n🛑 وقف الخسارة: [السعر]\n🎯 الهدف 1: [السعر]\n🎯 الهدف 2: [السعر]\n✅ الثقة: [النسبة]%\n📝 ملاحظة: [جملة واحدة]"}
            ]
        }]
    }
    response = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=body)
    return response.json()["content"][0]["text"]

@app.route("/telegram", methods=["POST"])
def telegram_webhook():
    data = request.json
    if not data:
        return jsonify({"ok": True})
    update_id = data.get("update_id")
    if update_id in processed_updates:
        return jsonify({"ok": True})
    processed_updates.add(update_id)
    message = data.get("message", {})
    photo = message.get("photo")
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "")
    if text == "/start":
        send_message(chat_id, "👋 أهلاً! أرسل لي صورة الشارت وأحللها فوراً 📊")
        return jsonify({"ok": True})
    if photo and chat_id:
        file_id = photo[-1]["file_id"]
        file_path = requests.get(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}").json()["result"]["file_path"]
        img = requests.get(f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}").content
        img_base64 = base64.b64encode(img).decode("utf-8")
        send_message(chat_id, "⏳ جاري تحليل الشارت...")
        try:
            analysis = analyze_chart(img_base64)
            send_message(chat_id, analysis)
        except Exception as e:
            send_message(chat_id, f"❌ خطأ: {str(e)}")
    return jsonify({"ok": True})

@app.route("/", methods=["GET"])
def home():
    return "البوت يعمل!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

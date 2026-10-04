import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TOKEN = os.environ.get("MAX_BOT_TOKEN", "")
WEBHOOK_SECRET = os.environ.get("WEBHOOK_SECRET", "")
CHANNEL_URL = "https://max.ru/se14525189_biz"
API = "https://platform-api2.max.ru"

HEADERS = {
    "Authorization": TOKEN,
    "Content-Type": "application/json",
}

def kb(rows):
    return [{
        "type": "inline_keyboard",
        "payload": {"buttons": rows}
    }]

def cb(text, payload):
    return {"type": "callback", "text": text, "payload": payload}

def link(text, url):
    return {"type": "link", "text": text, "url": url}

MAIN_BUTTONS = [
    [cb("🧪 8 класс", "grade_8"), cb("⚗️ 9 класс", "grade_9")],
    [cb("🔬 10 класс", "grade_10"), cb("🧬 11 класс", "grade_11")],
    [cb("🎓 ОГЭ", "oge"), cb("🏆 ЕГЭ", "ege")],
    [cb("🎮 Игры и тесты", "games")],
    [cb("✍️ Записаться на занятия", "signup")],
    [link("📢 Наш канал", CHANNEL_URL)],
]

WELCOME = (
    "🧪 Уроки химии | с Надеждой Романовной\n\n"
    "Привет! 👋 Я помогу разобраться в химии, повторить школьные темы "
    "и подготовиться к ОГЭ и ЕГЭ.\n\n"
    "Выберите нужный раздел:"
)

SECTIONS = {
    "grade_8": ("🧪 8 класс", "Здесь будут темы 8 класса: формулы, валентность, степень окисления, реакции, классы неорганических веществ и задания."),
    "grade_9": ("⚗️ 9 класс", "Здесь будут темы 9 класса, задания и тренировки."),
    "grade_10": ("🔬 10 класс", "Здесь будут материалы по органической химии и задания 10 класса."),
    "grade_11": ("🧬 11 класс", "Здесь будут повторение общей химии и задания 11 класса."),
    "oge": ("🎓 Подготовка к ОГЭ", "Здесь появятся теория, задания по линиям ОГЭ, мини-тесты и разборы."),
    "ege": ("🏆 Подготовка к ЕГЭ", "Здесь появятся теория, задания ЕГЭ, расчётные задачи и разборы."),
    "games": ("🎮 Игры и тесты", "Скоро здесь появятся химические мини-игры, тесты и переходы к играм на сайте."),
    "signup": ("✍️ Записаться на занятия", "Для записи на занятия напишите Надежде Романовне в MAX. Позже здесь сделаем полноценную форму записи."),
}

def send_to_user(user_id, text, buttons=None):
    body = {"text": text}
    if buttons:
        body["attachments"] = kb(buttons)
    r = requests.post(
        f"{API}/messages",
        params={"user_id": user_id},
        headers=HEADERS,
        json=body,
        timeout=20,
    )
    r.raise_for_status()
    return r.json()

def answer_callback(callback_id, text, buttons=None):
    body = {"message": {"text": text}}
    if buttons:
        body["message"]["attachments"] = kb(buttons)
    r = requests.post(
        f"{API}/answers",
        params={"callback_id": callback_id},
        headers=HEADERS,
        json=body,
        timeout=20,
    )
    r.raise_for_status()
    return r.json()

def find_user_id(data):
    # message_created / bot_started structures can differ by event.
    candidates = [
        data.get("user"),
        data.get("message", {}).get("sender"),
        data.get("callback", {}).get("user"),
        data.get("callback", {}).get("message", {}).get("sender"),
    ]
    for obj in candidates:
        if isinstance(obj, dict) and obj.get("user_id"):
            return obj["user_id"]
    return None

@app.get("/")
def home():
    return "MAX Chemistry Bot is running", 200

@app.post("/webhook")
def webhook():
    if WEBHOOK_SECRET:
        got = request.headers.get("X-Max-Bot-Api-Secret", "")
        if got != WEBHOOK_SECRET:
            return jsonify({"ok": False}), 403

    data = request.get_json(silent=True) or {}
    update_type = data.get("update_type", "")

    try:
        if update_type in ("bot_started", "message_created"):
            user_id = find_user_id(data)
            text = (data.get("message", {}).get("body", {}) or {}).get("text", "") or ""
            if user_id and (update_type == "bot_started" or text.strip().lower() in ("/start", "старт", "меню", "")):
                send_to_user(user_id, WELCOME, MAIN_BUTTONS)
            elif user_id:
                send_to_user(user_id, "Выберите раздел в меню 👇", MAIN_BUTTONS)

        elif update_type == "message_callback":
            callback = data.get("callback", {}) or {}
            payload = callback.get("payload", "")
            callback_id = callback.get("callback_id")
            if callback_id:
                if payload == "menu":
                    answer_callback(callback_id, WELCOME, MAIN_BUTTONS)
                elif payload in SECTIONS:
                    title, description = SECTIONS[payload]
                    answer_callback(
                        callback_id,
                        f"{title}\n\n{description}",
                        [[cb("⬅️ Главное меню", "menu")]]
                    )
                else:
                    answer_callback(callback_id, "Раздел скоро будет доступен.", [[cb("⬅️ Главное меню", "menu")]])
    except Exception as e:
        # Webhook should still answer quickly so MAX does not repeatedly redeliver it.
        print("Webhook processing error:", repr(e))

    return jsonify({"ok": True}), 200

@app.get("/setup")
def setup():
    """Open once after deploy to subscribe the bot to the webhook."""
    if not TOKEN:
        return jsonify({"ok": False, "error": "MAX_BOT_TOKEN is missing"}), 500
    public_url = os.environ.get("PUBLIC_URL") or os.environ.get("RENDER_EXTERNAL_URL")
    if not public_url:
        return jsonify({"ok": False, "error": "PUBLIC_URL/RENDER_EXTERNAL_URL is missing"}), 500
    if not WEBHOOK_SECRET:
        return jsonify({"ok": False, "error": "WEBHOOK_SECRET is missing"}), 500

    body = {
        "url": public_url.rstrip("/") + "/webhook",
        "update_types": ["message_created", "message_callback", "bot_started"],
        "secret": WEBHOOK_SECRET,
    }
    r = requests.post(f"{API}/subscriptions", headers=HEADERS, json=body, timeout=20)
    return jsonify({"status": r.status_code, "max_response": r.json() if r.content else {}}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "10000")))

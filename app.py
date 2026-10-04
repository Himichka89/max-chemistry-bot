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

GRADE8_BUTTONS = [
    [cb("🔬 Первые шаги в химии", "g8_intro")],
    [cb("⚛️ Строение атома", "g8_atom"), cb("🔗 Химическая связь", "g8_bond")],
    [cb("➕➖ Степень окисления", "g8_oxidation")],
    [cb("🧪 Простые и сложные вещества", "g8_substances")],
    [cb("🧩 Оксиды, кислоты, основания и соли", "g8_classes")],
    [cb("⚗️ Химические реакции", "g8_reactions")],
    [cb("✏️ Расставляем коэффициенты", "g8_coefficients")],
    [cb("🧮 Расчётные задачи", "g8_calculations")],
    [cb("🎮 Игры и тесты", "g8_games"), cb("🏆 Проверь себя", "g8_check")],
    [cb("⬅️ Главное меню", "menu")],
]

GRADE8_TEXT = (
    "🧪 Химия — 8 класс\n\n"
    "Выберите тему 👇\n"
    "Будем изучать теорию небольшими шагами, выполнять задания и проверять себя."
)

GRADE8_TOPICS = {
    "g8_intro": (
        "🔬 Первые шаги в химии",
        "Химия изучает вещества, их состав, строение, свойства и превращения.\n\n"
        "Начнём с наблюдения: вода, железо, кислород и поваренная соль — вещества. "
        "А стакан, гвоздь и ложка — физические тела, изготовленные из веществ.\n\n"
        "🎯 Мини-задание: что из списка является веществом?\n"
        "А) стеклянный стакан\nБ) алюминий\nВ) железный гвоздь"
    ),
    "g8_atom": (
        "⚛️ Строение атома",
        "Атом состоит из ядра и электронной оболочки. В ядре находятся протоны и нейтроны, "
        "а вокруг ядра — электроны.\n\n"
        "Число протонов равно порядковому номеру элемента. В нейтральном атоме число электронов "
        "равно числу протонов.\n\n"
        "🎯 Задание: сколько протонов и электронов в нейтральном атоме кислорода (Z = 8)?"
    ),
    "g8_bond": (
        "🔗 Химическая связь",
        "Атомы соединяются друг с другом благодаря химической связи. "
        "В 8 классе особенно важно научиться различать ионную и ковалентную связь.\n\n"
        "🎯 Задание: предположите, какая связь образуется в NaCl и почему."
    ),
    "g8_oxidation": (
        "➕➖ Степень окисления",
        "Степень окисления — условный заряд атома в соединении. "
        "У простых веществ она равна 0. У кислорода в большинстве соединений −2, "
        "у водорода обычно +1. Сумма степеней окисления в нейтральном веществе равна 0.\n\n"
        "🎯 Определите степени окисления элементов в H₂SO₄."
    ),
    "g8_substances": (
        "🧪 Простые и сложные вещества",
        "Простые вещества состоят из атомов одного химического элемента: O₂, Fe, S₈. "
        "Сложные вещества состоят из атомов разных элементов: H₂O, CO₂, NaCl.\n\n"
        "🎯 Найдите лишнее: O₂, H₂, H₂O, N₂."
    ),
    "g8_classes": (
        "🧩 Основные классы неорганических веществ",
        "Будем учиться узнавать оксиды, кислоты, основания и соли по формулам, "
        "называть вещества и составлять их формулы.\n\n"
        "🎯 Распределите по классам: CaO, HCl, NaOH, Na₂SO₄."
    ),
    "g8_reactions": (
        "⚗️ Химические реакции",
        "При химической реакции одни вещества превращаются в другие. "
        "Признаками реакции могут быть выделение газа, образование осадка, изменение цвета, "
        "выделение или поглощение тепла.\n\n"
        "🎯 Какой признак реакции можно наблюдать при взаимодействии кислоты с карбонатом?"
    ),
    "g8_coefficients": (
        "✏️ Расставляем коэффициенты",
        "Закон сохранения массы требует, чтобы число атомов каждого элемента слева и справа "
        "в уравнении было одинаковым.\n\n"
        "🎯 Расставьте коэффициенты: Al + O₂ → Al₂O₃."
    ),
    "g8_calculations": (
        "🧮 Расчётные задачи",
        "Здесь будем тренировать относительную молекулярную массу, количество вещества, "
        "молярную массу и простые расчёты по формулам.\n\n"
        "🎯 Найдите Mr(H₂O), если Ar(H)=1, Ar(O)=16."
    ),
    "g8_games": (
        "🎮 Игры и тесты",
        "Здесь будут короткие химические игры: «Угадай вещество», «Собери формулу», "
        "«Найди ошибку» и мини-тесты. Раздел будем наполнять постепенно."
    ),
    "g8_check": (
        "🏆 Проверь себя",
        "Мини-проверка по 8 классу:\n\n"
        "1. Что изучает химия?\n"
        "2. Сколько электронов у нейтрального атома с Z=12?\n"
        "3. Какая степень окисления у простого вещества?\n"
        "4. К какому классу относится CaO?\n"
        "5. Расставьте коэффициенты: H₂ + O₂ → H₂O."
    ),
}

def grade8_topic_buttons():
    return [
        [cb("📖 К темам 8 класса", "grade_8")],
        [cb("⬅️ Главное меню", "menu")],
    ]

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
                elif payload == "grade_8":
                    answer_callback(callback_id, GRADE8_TEXT, GRADE8_BUTTONS)
                elif payload in GRADE8_TOPICS:
                    title, description = GRADE8_TOPICS[payload]
                    answer_callback(
                        callback_id,
                        f"{title}\n\n{description}",
                        grade8_topic_buttons()
                    )
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

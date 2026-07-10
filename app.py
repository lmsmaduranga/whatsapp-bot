import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "MySecretToken123")

# 🔐 Fetch secure credentials from Render Environment Variables
ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

print("========== APP STARTED ==========")
print("ACCESS TOKEN:", "OK" if ACCESS_TOKEN else "MISSING")
print("PHONE NUMBER ID:", PHONE_NUMBER_ID if PHONE_NUMBER_ID else "MISSING")
print("GEMINI KEY:", "OK" if GEMINI_API_KEY else "MISSING")

# 🏢 System instruction updated with Russian language restriction
system_instruction = """
You are the expert B2B Export Trade Manager for Al Awali Trading Co LLC Head Office based in Dubai, UAE.

We import premium fabric rolls globally and export wholesale fabric supplies to GCC countries (Saudi Arabia, Oman, Qatar, Kuwait, Bahrain, UAE) and worldwide.

Products:
- Cotton Single Jersey
- Denim Rolls
- Polyester
- Spandex

Rules for Responding:
1. Strictly respond ONLY in the customer's choice among these four languages: English, Arabic, Hindi, or Russian. Do not use any other languages.
2. Keep replies short, professional, polite, and completely business-focused (Under 3 sentences).
3. We sell only wholesale fabric rolls/bales. MOQ is 1 pallet or container. We do NOT sell individual items, garments, or small retail quantities.
4. Never invent stock numbers or precise custom pricing. Ask them to provide specific item codes or industrial material specifications so we can verify manually.
"""

# 📝 Welcome Message with 4 Languages
WELCOME_MESSAGE = (
    "👋 Welcome to Al Awali Trading Co. LLC.\n\n"
    "Thank you for contacting us.\n\n"
    "We are a trusted textile trading company based in the UAE, specializing in sourcing and supplying high-quality fabrics and textile products from leading manufacturers around the world.\n\n"
    "To continue, please select your preferred language:\n"
    "🇬🇧 1. English\n"
    "🇦🇪 2. العربية (Arabic)\n"
    "🇮🇳 3. हिन्दी / اردو (Hindi / Urdu)\n"
    "🇷🇺 4. Русский (Russian)"
)

# 📝 English Main Menu
MAIN_MENU_EN = (
    "How can we assist you today?\n\n"
    "1️⃣ Browse Fabric Collections\n"
    "2️⃣ Request a Fabric Quotation\n"
    "3️⃣ Wholesale / Bulk Order Inquiry\n"
    "4️⃣ Check Product Availability\n"
    "5️⃣ Send Fabric Sample / Reference Image\n"
    "6️⃣ Delivery & Shipping Information\n"
    "7️⃣ Our Location 📍\n"
    "8️⃣ Contact Our Sales Team\n\n"
    "9️⃣ Back to Language Menu"
)

# 📝 Arabic Main Menu
MAIN_MENU_AR = (
    "كيف يمكننا مساعدتك اليوم؟\n\n"
    "1️⃣ تصفح مجموعات الأقمشة\n"
    "2️⃣ طلب عرض سعر للأقمشة\n"
    "3️⃣ استفسار عن طلبات الجملة / الكميات الكبيرة\n"
    "4️⃣ التحقق من توفر المنتج\n"
    "5️⃣ إرسال عينة قماش / صورة مرجعية\n"
    "6️⃣ معلومات التوصيل والشحن\n"
    "7️⃣ موقعنا 📍\n"
    "8️⃣ الاتصال بفريق المبيعات لدينا\n\n"
    "9️⃣ العودة إلى قائمة اللغة"
)

# 📝 Hindi Main Menu
MAIN_MENU_HI = (
    "आज हम आपकी क्या सहायता कर सकते हैं?\n\n"
    "1️⃣ फैब्रिक कलेक्शन देखें\n"
    "2️⃣ फैब्रिक कोटेशन के लिए अनुरोध करें\n"
    "3️⃣ थोक / बल्क ऑर्डर पूछताछ\n"
    "4️⃣ उत्पाद की उपलब्धता जांचें\n"
    "5️⃣ फैब्रिक सैंपल / संदर्भ छवि भेजें\n"
    "6️⃣ डिलीवरी और शिपिंग की जानकारी\n"
    "7️⃣ हमारा स्थान 📍\n"
    "8️⃣ हमारी बिक्री टीम से संपर्क करें\n\n"
    "9️⃣ भाषा मेनू पर वापस जाएं"
)

# 📝 Russian Main Menu
MAIN_MENU_RU = (
    "Как мы можем помочь вам сегодня?\n\n"
    "1️⃣ Посмотреть коллекции тканей\n"
    "2️⃣ Запросить прайс-лист / коммерческое предложение\n"
    "3️⃣ Оптовые закупки / Большие заказы\n"
    "4️⃣ Проверить наличие товара\n"
    "5️⃣ Отправить образец ткани / Изображение\n"
    "6️⃣ Информация о доставке и логистике\n"
    "7️⃣ Наше местоположение 📍\n"
    "8️⃣ Связаться с отделом продаж\n\n"
    "9️⃣ Вернуться к выбору языка"
)

# =========================
# HOME CHECK
# =========================
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "service": "Al Awali WhatsApp Bot"
    }), 200

# =========================
# GEMINI AI
# =========================
def get_gemini_response(message):
    if not GEMINI_API_KEY:
        return "Sorry, AI service is temporarily unavailable."

    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": message}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        }
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print("========== GEMINI RESPONSE ==========")
        print(response.status_code)
        
        data = response.json()

        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"]

        return "Thank you for contacting Al Awali Trading Co LLC."

    except Exception as e:
        print("Gemini Error:", e)
        return "Thank you for contacting Al Awali Trading Co LLC."

# =========================
# WHATSAPP SEND TEXT
# =========================
def send_whatsapp_message(to, text):
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("WhatsApp credentials missing")
        return

    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }

    response = requests.post(url, json=payload, headers=headers)
    print("========== WHATSAPP SEND ==========")
    print(response.status_code)

# =========================
# LOCATION CARD
# =========================
def send_location(to):
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("WhatsApp credentials missing")
        return

    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "location",
        "location": {
            "latitude": 25.2694,
            "longitude": 55.3023,
            "name": "Al Awali Trading Co LLC Head Office",
            "address": "Al Sabkha, Deira, Dubai, United Arab Emirates"
        }
    }

    response = requests.post(
        url,
        json=payload,
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
    )

    print("========== LOCATION RESPONSE ==========")
    print(response.status_code)

# =========================
# VERIFY WEBHOOK
# =========================
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200

    return "Forbidden", 403

# =========================
# RECEIVE MESSAGE
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():
    print("========== WEBHOOK HIT ==========")
    data = request.get_json()
    print(data)

    try:
        value = data["entry"][0]["changes"][0]["value"]

        if "messages" not in value:
            return jsonify({"status": "ignored"}), 200

        message = value["messages"][0]
        sender = message["from"]
        msg_type = message["type"]

        if msg_type == "text":
            user_text = message["text"]["body"].lower().strip()
            print("USER:", user_text)

            # 1. Greeting Check
            greeting_keywords = ["hi", "hello", "hey", "salam", "assalamualaikum", "assalam", "привет", "здравствуйте"]
            if any(word == user_text for word in greeting_keywords) or user_text.startswith("assalamualaikum"):
                send_whatsapp_message(sender, WELCOME_MESSAGE)
                return jsonify({"status": "success"}), 200

            # 2. Language Selection routing (1, 2, 3, or 4) OR Back to Menu option (9)
            if user_text in ["1", "1."]:
                send_whatsapp_message(sender, MAIN_MENU_EN)
                return jsonify({"status": "success"}), 200
            elif user_text in ["2", "2."]:
                send_whatsapp_message(sender, MAIN_MENU_AR)
                return jsonify({"status": "success"}), 200
            elif user_text in ["3", "3."]:
                send_whatsapp_message(sender, MAIN_MENU_HI)
                return jsonify({"status": "success"}), 200
            elif user_text in ["4", "4."]:
                send_whatsapp_message(sender, MAIN_MENU_RU)
                return jsonify({"status": "success"}), 200
            elif user_text in ["9", "9."]:
                send_whatsapp_message(sender, WELCOME_MESSAGE)
                return jsonify({"status": "success"}), 200

            # 3. Main Menu Option 7 Check -> Send Location Card
            if user_text in ["7", "7.", "location", "address", "पता", "موقع", "عنوان", "адрес", "где вы"]:
                send_location(sender)
                reply = get_gemini_response("The customer requested the office location. Respond politely in 1 short sentence confirming that the location map card has been shared above.")
                send_whatsapp_message(sender, reply)
                return jsonify({"status": "success"}), 200

            # 4. Handle other menu numbers or regular text via Gemini AI
            menu_mapping = {
                "1": "The customer wants to browse fabric collections.",
                "2": "The customer is requesting a fabric quotation.",
                "3": "The customer is inquiring about wholesale / bulk orders.",
                "4": "The customer wants to check product availability.",
                "5": "The customer wants to send a fabric sample or reference image.",
                "6": "The customer is asking about delivery and shipping information.",
                "8": "The customer wants to contact our sales team directly."
            }

            clean_num = user_text.replace(".", "")
            if clean_num in menu_mapping:
                ai_prompt = f"{menu_mapping[clean_num]} Provide a brief, professional response matching the language style they used."
                reply = get_gemini_response(ai_prompt)
            else:
                reply = get_gemini_response(message["text"]["body"])

            send_whatsapp_message(sender, reply)

        else:
            send_whatsapp_message(
                sender,
                "Thank you for contacting Al Awali Trading Co LLC. Our team will assist you shortly."
            )

    except Exception as e:
        print("WEBHOOK ERROR:", e)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

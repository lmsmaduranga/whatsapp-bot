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

# 🏢 System instruction updated
system_instruction = """
You are the expert B2B Export Trade Manager for Al Awali Trading Co LLC Head Office based in Dubai, UAE.
We import premium fabric rolls globally and export wholesale fabric supplies to GCC countries and worldwide.
Rules for Responding:
1. Strictly respond ONLY in the customer's choice among these four languages: English, Arabic, Hindi, or Russian.
2. Keep replies short, professional, polite, and completely business-focused (Under 3 sentences).
3. We sell only wholesale fabric rolls/bales. MOQ is 1 pallet or container. We do NOT sell small retail quantities.
4. If they ask about fabric details, tell them to contact sales team or provide item codes.
"""

# ==============================================================================
# HARDCODED MULTILINGUAL MENUS (Fixed with A, B, C, D for Language)
# ==============================================================================

WELCOME_MESSAGE = (
    "👋 Welcome to Al Awali Trading Co. LLC.\n\n"
    "Thank you for contacting us.\n\n"
    "We are a trusted textile trading company based in the UAE, specializing in sourcing and supplying high-quality fabrics and textile products from leading manufacturers around the world.\n\n"
    "To continue, please select your preferred language:\n"
    "🇬🇧 A. English\n"
    "🇦🇪 B. العربية (Arabic)\n"
    "🇮🇳 C. हिन्दी / اردو (Hindi / Urdu)\n"
    "🇷🇺 D. Русский (Russian)"
)

# --- 1. MAIN MENUS ---
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

# --- 2. FABRIC CATEGORIES MENUS ---
FABRIC_MENU_EN = (
    "🧵 *Our Fabric Collections*\n"
    "Please select the type of fabric you are looking for:\n\n"
    "1️⃣ Abaya & Black Fabrics\n"
    "2️⃣ Dress & Fashion Fabrics\n"
    "3️⃣ Cotton Fabrics\n"
    "4️⃣ Linen Fabrics\n"
    "5️⃣ Silk Fabrics\n"
    "6️⃣ Embroidery & Designer Fabrics\n"
    "7️⃣ Suiting Fabrics\n"
    "8️⃣ Other Fabrics\n\n"
    "↩️ Reply *0* to go Back to Main Menu\n\n"
    "Please select a category number or send us a photo of the fabric you need."
)

# --- 3. SAMPLE FABRIC DETAILS ---
SAMPLE_DETAILS_EN = (
    "ℹ️ *Fabric Details (Sample Specification)*\n\n"
    "🧵 *Fabric Name:* Premium Al Awali Selection\n"
    "🎨 *Available Colors:* Black, Navy, White, Beige, Crimson\n"
    "📏 *Width:* 58 / 60 inches\n"
    "📦 *Minimum Order Quantity (MOQ):* 1 Pallet / Container (Wholesale Bulk)\n\n"
    "👉 To request prices or a physical sample, please reply with *8* to connect directly with our Sales Team, or send us a picture of your target fabric."
)


# ==============================================================================
# CORE ROUTINES
# ==============================================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running", "service": "Al Awali WhatsApp Bot"}), 200


def get_gemini_response(message):
    if not GEMINI_API_KEY:
        return "Sorry, AI service is temporarily unavailable."
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": message}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        data = response.json()
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return "Thank you for contacting Al Awali Trading Co LLC."
    except Exception as e:
        print("Gemini Error:", e)
        return "Thank you for contacting Al Awali Trading Co LLC."


def send_whatsapp_message(to, text):
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("WhatsApp credentials missing")
        return
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    requests.post(url, json=payload, headers=headers)


def send_location(to):
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        return
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp", "to": to, "type": "location",
        "location": {
            "latitude": 25.2694, "longitude": 55.3023,
            "name": "Al Awali Trading Co LLC Head Office",
            "address": "Al Sabkha, Deira, Dubai, United Arab Emirates"
        }
    }
    requests.post(url, json=payload, headers={"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"})


# ==============================================================================
# WEBHOOK RECEIVE & STATE HANDLING
# ==============================================================================

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    try:
        value = data["entry"][0]["changes"][0]["value"]
        if "messages" not in value:
            return jsonify({"status": "ignored"}), 200

        message = value["messages"][0]
        sender = message["from"]
        msg_type = message["type"]

        if msg_type == "text":
            user_text = message["text"]["body"].strip().lower()
            clean_num = user_text.replace(".", "")

            # 1. Greeting Triggers -> Send Language Choice Welcome Menu (A, B, C, D)
            greeting_keywords = ["hi", "hello", "hey", "salam", "assalamualaikum", "assalam", "привет", "здравствуйте"]
            if any(word == user_text for word in greeting_keywords) or user_text.startswith("assalamualaikum"):
                send_whatsapp_message(sender, WELCOME_MESSAGE)
                return jsonify({"status": "success"}), 200

            # 2. Language Selection Routing using Letters (A, B, C, D) to avoid conflicts
            if clean_num in ["a", "а"]:  # handles both english and russian character 'a'
                send_whatsapp_message(sender, MAIN_MENU_EN)
                return jsonify({"status": "success"}), 200
            elif clean_num == "b":
                send_whatsapp_message(sender, MAIN_MENU_AR)
                return jsonify({"status": "success"}), 200
            elif clean_num == "c":
                send_whatsapp_message(sender, MAIN_MENU_HI)
                return jsonify({"success": "success"}), 200
            elif clean_num == "d":
                send_whatsapp_message(sender, MAIN_MENU_RU)
                return jsonify({"status": "success"}), 200

            # 3. Main Menu Option Selection Logic (1 to 9)
            if clean_num == "1":
                # User selected Option 1: Browse Fabric Collections
                send_whatsapp_message(sender, FABRIC_MENU_EN)
                return jsonify({"status": "success"}), 200
            
            elif clean_num == "7" or user_text in ["location", "address", "पता", "موقع", "عنوان", "адрес"]:
                # User selected Option 7: Location
                send_location(sender)
                reply = get_gemini_response("The customer requested the office location. Respond politely in 1 short sentence confirming that the location map card has been shared above.")
                send_whatsapp_message(sender, reply)
                return jsonify({"status": "success"}), 200
                
            elif clean_num == "9":
                # User selected Option 9: Back to Language Menu
                send_whatsapp_message(sender, WELCOME_MESSAGE)
                return jsonify({"status": "success"}), 200
                
            elif clean_num == "0":
                # User selected Back inside Submenus
                send_whatsapp_message(sender, MAIN_MENU_EN)
                return jsonify({"status": "success"}), 200

            # If user inputs inside fabric subcategories (choices 2 to 8)
            if clean_num in ["2", "3", "4", "5", "6", "7", "8"]:
                # Let's map option 8 to Sales team directly, others to sample spec card
                if clean_num == "8":
                    reply = get_gemini_response("The customer wants to contact our sales team directly.")
                    send_whatsapp_message(sender, reply)
                else:
                    send_whatsapp_message(sender, SAMPLE_DETAILS_EN)
                return jsonify({"status": "success"}), 200

            # 4. Global keywords and Gemini fallback
            reply = get_gemini_response(message["text"]["body"])
            send_whatsapp_message(sender, reply)

        elif msg_type == "image":
            reply = get_gemini_response("The user sent an image reference for a fabric. Respond politely stating that our trade managers will verify availability shortly.")
            send_whatsapp_message(sender, reply)
        else:
            send_whatsapp_message(sender, "Thank you for contacting Al Awali Trading Co LLC. Our team will assist you shortly.")

    except Exception as e:
        print("WEBHOOK ERROR:", e)

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

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

# 🏢 System instruction restricted strictly to English, Arabic, and Hindi
system_instruction = """
You are the expert B2B Export Trade Manager for Al Awali Trading Co LLC Head Office based in Dubai, UAE.

We import premium fabric rolls globally and export wholesale fabric supplies to GCC countries (Saudi Arabia, Oman, Qatar, Kuwait, Bahrain, UAE) and worldwide.

Products:
- Cotton Single Jersey
- Denim Rolls
- Polyester
- Spandex

Rules for Responding:
1. Strictly respond ONLY in the customer's choice among these three languages: English, Arabic, or Hindi. Do not use any other languages.
2. Keep replies short, professional, polite, and completely business-focused (Under 3 sentences).
3. We sell only wholesale fabric rolls/bales. MOQ is 1 pallet or container. We do NOT sell individual items, garments, or small retail quantities.
4. Never invent stock numbers or precise custom pricing. Ask them to provide specific item codes or industrial material specifications so we can verify manually.
"""

# 📝 Exact Custom Welcome Message requested by you
WELCOME_MESSAGE = (
    "👋 Welcome to Al Awali Fabrics!\n\n"
    "Thank you for contacting us.\n\n"
    "We are delighted to assist you with our premium collection of fabrics and textiles for retail and wholesale customers. "
    "Our team is committed to helping you find the perfect fabric for your fashion, tailoring, and business needs.\n\n"
    "Please let us know how we can assist you today, and we'll be happy to help."
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
# LOCATION CARD (Al Awali Trading Co LLC Head Office)
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

            # 1. Greeting Check (Triggers your custom Welcome Message immediately)
            greeting_keywords = ["hi", "hello", "hey", "salam", "assalamualaikum", "assalam"]
            
            if any(word == user_text for word in greeting_keywords) or user_text.startswith("assalamualaikum"):
                send_whatsapp_message(sender, WELCOME_MESSAGE)
                return jsonify({"status": "success"}), 200

            # 2. Location Check (Triggers the custom location map card)
            location_keywords = ["location", "address", "पता", "लोकेशन", "موقع", "عنوان"]
            
            if any(word in user_text for word in location_keywords):
                send_location(sender)
                reply = get_gemini_response("The customer asked for the office location. Respond politely in 1 short sentence stating that we have shared our official location card above.")
                send_whatsapp_message(sender, reply)
            
            # 3. Regular Inquiries passed directly to Gemini AI
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

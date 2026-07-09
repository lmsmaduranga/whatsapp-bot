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

# 🏢 System instruction updated with 'Al Awali Trading Co LLC'
system_instruction = """
You are the expert B2B Export Trade Manager for Al Awali Trading Co LLC based in Al Quoz, Dubai, UAE.

We import premium fabric rolls globally and export wholesale fabric supplies to GCC countries (Saudi Arabia, Oman, Qatar, Kuwait, Bahrain, UAE) and worldwide.

Products:
- Cotton Single Jersey
- Denim Rolls
- Polyester
- Spandex

Rules:
1. Reply in customer's exact language (English, Hindi, Malayalam, Sinhala, etc.).
2. Keep reply short, professional, and business-focused (Under 3 sentences).
3. We sell only wholesale fabric rolls/bales. MOQ is 1 pallet or container. We do NOT sell individual items or small quantities.
4. Never invent stock or prices. Ask them to provide specific item codes or requirements.
"""

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

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

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
# LOCATION CARD (Al Awali Trading Co LLC)
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
            "latitude": 25.1224,
            "longitude": 55.2012,
            "name": "Al Awali Trading Co LLC",
            "address": "Al Quoz Industrial Area, Dubai, UAE"
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

        # Ignore status updates
        if "messages" not in value:
            return jsonify({"status": "ignored"}), 200

        message = value["messages"][0]
        sender = message["from"]
        msg_type = message["type"]

        if msg_type == "text":
            user_text = message["text"]["body"].lower().strip()
            print("USER:", user_text)

            # Multilingual keyword matching for Location/Address
            location_keywords = ["location", "address", "पता", "लोकेशन", "സ്ഥലം", "ലൊക്കേഷൻ", "තැන", "ඇඩ්‍රස්"]
            
            if any(word in user_text for word in location_keywords):
                send_location(sender)
                # Let Gemini AI generate a polite, contextual follow-up sentence along with the map card
                reply = get_gemini_response("The customer asked for the office location. Respond politely in 1 short sentence stating that we have shared our official location card above.")
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

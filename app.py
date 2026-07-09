import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = "MySecretToken123"

# 🔐 Render Environment Variables
ACCESS_TOKEN = os.environ.get("EAAUx74tjPN8BRznZBFdCLalPQvOZA6qu80QwS0XYnnFAZB6FZAB013cXIMj4r9eCReXdPZBByUuUHvnPw4bw0gKNFfB41tUrnwVWepc6F7af3BCFScok6jHoChPkpQCZADjSbnyBeQ5EtifUq600ZCU0uoWtAzL90R00lpI8qF8H1Kttu19KocJPeItWAx2s1aozg3RoXfB7mAcmXYakGegb3uMdZCO8y7Y2ZBfeIxZCgFeA4ZCCyJIz4kSp7k5poZC8ZBnR3dtMcbblZCliXRxF1ZCJmAmrjsQ")
PHONE_NUMBER_ID = os.environ.get("1272291502625274")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

system_instruction = (
    "You are the expert B2B Export Trade Manager for 'Awali International Textile Trading' based in Al Quoz, Dubai, UAE. "
    "We import premium Fabric Rolls globally and export/supply to GCC countries (Saudi Arabia, Oman, Qatar, Kuwait, Bahrain, UAE) and worldwide. "
    "We only sell in wholesale bulk (Fabric Rolls/Bales), minimum order quantity (MOQ) is 1 Pallet or Container. We do NOT sell individual garments or clothing. "
    "Our main products are Cotton Single Jersey, Denim Rolls, Polyester, and Spandex. "
    "Rules for responding:\n"
    "1. Always reply in the exact language the customer used (English, Hindi, or Malayalam).\n"
    "2. Be extremely professional, polite, and brief (Keep responses short, business-focused, and under 3 sentences).\n"
    "3. If they ask about Location, Price, Delivery, Stock, or Quotation, give professional guidance. "
    "Do not invent specific stock numbers, ask them to provide item codes or product details so we can check."
)

# 🤖 100% Corrected Gemini API Request Function
def get_gemini_response(user_message):
    if not GEMINI_API_KEY:
        return "⚠️ Gemini API Key එක Render එකේ සෙට් කරලා නැහැ මචං!"
    
    # Gemini 1.5 Flash නිවැරදිම Endpoint එක
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    
    # 📝 නිල Documentation එකට අනුව නිවැරදිම Payload Format එක
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_message}]
            }
        ],
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        res_json = response.json()
        
        # පිළිතුර සාර්ථකව ආවොත්
        if 'candidates' in res_json and len(res_json['candidates']) > 0:
            return res_json['candidates'][0]['content']['parts'][0]['text']
        else:
            # 🔴 ගූගල් එකෙන් වෙන මොකක් හරි Error එකක් එවුවොත් ඒක කෙලින්ම බලාගන්න පෙන්වන ක්‍රමය
            return f"❌ Gemini Error: {res_json.get('error', {}).get('message', 'Unknown Error')}"
            
    except Exception as e:
        return f"❌ Python Exception: {str(e)}"

# 💬 WhatsApp Text Message Sender
def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
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
    return response.json()

# 📍 WhatsApp Location Card Sender
def send_whatsapp_location(to, name, address, latitude=25.1224, longitude=55.2012):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "location",
        "location": {
            "latitude": latitude,     
            "longitude": longitude,   
            "name": name,             
            "address": address        
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

# 🖼️ WhatsApp Image Sender
def send_whatsapp_image(to, image_url, caption_text):
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "image",
        "image": {
            "link": image_url,        
            "caption": caption_text   
        }
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()


@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Forbidden", 403

@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.json
    try:
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            from_number = message["from"]
            msg_type = message["type"]

            # Voice Note ආවොත්
            if msg_type == "audio" or msg_type == "voice":
                voice_reply = (
                    "🎧 *We received your voice note!* Our trade managers will check it and reply shortly."
                )
                send_whatsapp_message(from_number, voice_reply)
                return jsonify({"status": "success"}), 200

            # Text මැසේජ් ආවොත්
            elif msg_type == "text":
                user_text = message["text"]["body"].lower().strip()
                
                # Location Keyword එකක් ආවොත්
                if any(word in user_text for word in ["location", "address", "पता", "लोकेशन", "സ്ഥലം", "ലൊക്കേഷൻ"]):
                    send_whatsapp_location(from_number, "Awali International Textile Trading", "Al Quoz Industrial Area, Dubai, UAE")
                    ai_reply = get_gemini_response("The customer asked for the office location. Respond politely in 1 short sentence that we sent the Google Maps location above.")
                    send_whatsapp_message(from_number, ai_reply)
                    return jsonify({"status": "success"}), 200
                
                # New Material Keyword එකක් ආවොත්
                elif any(word in user_text for word in ["new", "material", "नया", "പുതിയത്"]):
                    sample_image = "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600&auto=format&fit=crop"
                    ai_reply = get_gemini_response("The customer asked about new arrivals or materials. Give a polite 1-sentence update about our regular stock imports, and say we shared a sample image.")
                    send_whatsapp_image(from_number, sample_image, ai_reply)
                    return jsonify({"status": "success"}), 200

                # වෙනත් ඕනෑම මැසේජ් එකක් කෙලින්ම Gemini එකට
                else:
                    ai_reply = get_gemini_response(user_text)
                    send_whatsapp_message(from_number, ai_reply)
            
    except Exception as e:
        print("Error processing message:", e)
        
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

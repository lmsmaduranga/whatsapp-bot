import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = "MySecretToken123"

# ⚠️ ඔයාගේ Token සහ Phone Number ID එක මෙතනට දාන්න (දෙපැත්තේ r" " සහ " " ලකුණු අනිවාර්යයි)
ACCESS_TOKEN = r"EAAUx74tjPN8BRZBTgILeRqjfvVllrZBL7lmRwbBv01jQxOUHZBK4jHFpvVGAY8WLiOpa9cWw5DgaCvFFpXMCLdz67G1qKf0ND7htPnZCAfZCoJPMVDJogFnwg2bZBNo7mv3Q862V2qGaI9Xc1PhmCR0YraXvpr9XZCCnmTcGZAJDTyCk4qFxZBjTRZCcsWJdxhH3k12BKZAAtZCel81BjZC9Sg2NvMuULkgLsCmq0MlH6JDNu8ftg7UcrZCs1ZAMNGKToODfxtqNIjs6RuTcwqvU1uzx2gmwcME"
PHONE_NUMBER_ID = "1272291502625274"

# 1. 💬 සාමාන්‍ය Text මැසේජ් යවන ක්‍රමය
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

# 2. 📍 GOOGLE MAP LOCATION එකක් මැප් කාඩ් එකක් විදිහටම යවන ක්‍රමය
def send_whatsapp_location(to, name, address, latitude, longitude):
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

# 3. 🖼️ IMAGE (පින්තූර) එකක් විස්තර (Caption) එකක් එක්ක යවන ක්‍රමය
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
            print("WEBHOOK_VERIFIED")
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

            # ----------------------------------------------------
            # 🎙️ VOICE NOTE / AUDIO එකක් ආවොත් (භාෂා 3න්ම යයි)
            # ----------------------------------------------------
            if msg_type == "audio" or msg_type == "voice":
                voice_reply = (
                    "🎧 *We received your voice note!* Our trade managers will check it and reply shortly.\n\n"
                    "🎧 *हमें आपका वॉयस नोट मिल गया है!* हमारे सेल्स मैनेजर जल्द ही आपसे संपर्क करेंगे।\n\n"
                    "🎧 *ഞങ്ങൾക്ക് നിങ്ങളുടെ വോയ്‌സ് നോട്ട് ലഭിച്ചു!* ഞങ്ങളുടെ സെയിൽസ് ടീം ഉടൻ മറുപടി നൽകും."
                )
                send_whatsapp_message(from_number, voice_reply)
                return jsonify({"status": "success"}), 200

            # ----------------------------------------------------
            # 💬 TEXT මැසේජ් එකක් ආවොත් සිදුවන ක්‍රියාවලිය
            # ----------------------------------------------------
            elif msg_type == "text":
                user_text = message["text"]["body"].lower().strip()
                
                # ====================================================
                # A. ENGLISH LOGIC
                # ====================================================
                if user_text in ["hi", "hello", "price", "prices", "location", "address", "new", "new material", "agent"]:
                    if user_text in ["hi", "hello"]:
                        reply = (
                            "Welcome to *Awali International Textile Trading*! 🌐🧵\n"
                            "We import Fabric Rolls globally and supply to GCC.\n\n"
                            "Please reply with a keyword:\n"
                            "👉 *Price* - Wholesale Rates (AED/USD)\n"
                            "👉 *New* - View New Materials (with Images) 🖼️\n"
                            "👉 *Location* - Get Google Map Location 📍\n"
                            "👉 *Agent* - Talk to Sales Manager"
                        )
                        send_whatsapp_message(from_number, reply)
                    
                    elif user_text in ["price", "prices"]:
                        reply = (
                            "💰 *Wholesale Price List (Fabric Rolls):*\n\n"
                            "• Cotton Single Jersey: *From AED 12.50 per KG*\n"
                            "• Premium Denim (Rolls): *From AED 8.50 per Yard*\n"
                            "• Polyester Fabrics: *From AED 6.50 per Yard*\n\n"
                            "_*MOQ:* 1 Pallet / Container. Type *New* to see images!"
                        )
                        send_whatsapp_message(from_number, reply)
                    
                    elif user_text in ["location", "address"]:
                        send_whatsapp_location(
                            to=from_number,
                            name="Awali International Textile Trading",
                            address="Industrial Area, Dubai, UAE",
                            latitude=25.1972,   
                            longitude=55.2744
                        )
                    
                    elif user_text in ["new", "new material"]:
                        sample_image = "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600&auto=format&fit=crop"
                        caption = "✨ *NEW ARRIVAL: Premium Cotton Twill Rolls* ✨\n\n• GSM: 220\n• Width: 58/60 Inches\n• Price: *AED 14.50 per Meter*\n• Status: In Stock (Dubai Warehouse)"
                        send_whatsapp_image(from_number, sample_image, caption)
                    
                    elif user_text == "agent":
                        reply = "🤝 *Connecting to Export Team...* One of our B2B trade specialists will text you back shortly."
                        send_whatsapp_message(from_number, reply)

                # ====================================================
                # B. HINDI LOGIC (हिंदी)
                # ====================================================
                elif user_text in ["नमस्ते", "namaste", "दाम", "rate", "पता", "pata", "नया", "नया कपड़ा", "एजेंट"]:
                    if user_text in ["नमस्ते", "namaste"]:
                        reply = (
                            "*अवाली इंटरनेशनल टेक्सटाइल ट्रेडिंग* में आपका स्वागत है! 🌐🧵\n"
                            "हम वैश्विक स्तर पर फैब्रिक रोल का इम्पोर्ट और एक्सपोर्ट करते हैं।\n\n"
                            "कृपया नीचे दिए गए शब्द लिखकर रिप्लाई करें:\n"
                            "👉 *दाम* (Price) - होलसेल रेट लिस्ट\n"
                            "👉 *नया* (New) - नए कपड़े (फ़ोटो के साथ) 🖼️\n"
                            "👉 *पता* (Location) - गूगल मैप लोकेशन 📍\n"
                            "👉 *एजेंट* (Agent) - हमारे सेल्स टीम से बात करें"
                        )
                        send_whatsapp_message(from_number, reply)
                    
                    elif user_text in ["दाम", "rate"]:
                        reply = (
                            "💰 *होलसेल रेट लिस्ट (Fabric Rolls):*\n\n"
                            "• कॉटन सिंगल जर्सी: *AED 12.50 प्रति KG से शुरू*\n"
                            "• प्रीमियम डेनिम रोल: *AED 8.50 प्रति Yard से शुरू*\n"
                            "• पॉलिएस्टर फैब्रिक्स: *AED 6.50 प्रति Yard से शुरू*\n\n"
                            "तस्वीरें देखने के लिए *नया* लिखकर रिप्लाई करें!"
                        )
                        send_whatsapp_message(from_number, reply)
                    
                    elif user_text in ["पता", "pata"]:
                        send_whatsapp_location(
                            to=from_number,
                            name="Awali International Textile Trading",
                            address="Industrial Area, Dubai, UAE",
                            latitude=25.1972,   
                            longitude=55.2744
                        )
                    
                    elif user_text in ["नया", "नया कपड़ा"]:
                        sample_image = "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600&auto=format&fit=crop"
                        caption = "✨ *नया स्टॉक: प्रीमियम कॉटन टविल रोल* ✨\n\n• GSM: 220\n• चौड़ाई: 58/60 इंच\n• रेट: *AED 14.50 प्रति मीटर*\n• स्टॉक: दुबई वेयरहाउस में उपलब्ध है।"
                        send_whatsapp_image(from_number, sample_image, caption)
                    
                    elif user_text == "एजेंट":
                        reply = "🤝 *एक्सपोर्ट टीम से जुड़ रहे हैं...* हमारे बी2बी सेल्स एजेंट कुछ ही मिनटों में आपसे संपर्क करेंगे।"
                        send_whatsapp_message(from_number, reply)

                # ====================================================
                # C. MALAYALAM LOGIC (മലയാളം)
                # ====================================================
                elif user_text in ["ഹലോ", "namaskaram", "നമസ്കാരം", "വില", "price malayalam", "സ്ഥലം", "location malayalam", "പുതിയത്", "new malayalam", "ഏജന്റ്"]:
                    if user_text in ["ഹലോ", "നമസ്കാരം", "namaskaram"]:
                        reply = (
                            "അവാലി ഇന്റർനാഷണൽ ടെക്സ്റ്റൈൽ ട്രേഡിംഗിലേക്ക് സ്വാഗതം! 🌐🧵\n"
                            "ഞങ്ങൾ ഹോൾസെയിൽ ആയി ഫാബ്രിക് റോളുകൾ സപ്ലൈ ചെയ്യുന്നു.\n\n"
                            "വിവരങ്ങൾക്ക് താഴെയുള്ള വാക്കുകൾ ടൈപ്പ് ചെയ്യുക:\n"
                            "👉 *വില* (Price) - ഹോൾസെയിൽ നിരക്കുകൾ\n"
                            "👉 *പുതിയത്* (New) - പുതിയ സ്റ്റോക്കുകൾ (ചിത്രങ്ങൾ സഹിതം) 🖼️\n"
                            "👉 *സ്ഥലം* (Location) - ഗൂഗിൾ മാപ്പ് ലൊക്കേഷൻ 📍\n"
                            "👉 *ഏജന്റ്* (Agent) - സെയിൽസ് മാനേജരുമായി സംസാരിക്കാൻ"
                        )
                        send_whatsapp_message(from_number, reply)
                    
                    elif user_text in ["വില", "price malayalam"]:
                        reply = (
                            "💰 *ഹോൾസെയിൽ വിലവിവരം (Fabric Rolls):*\n\n"
                            "• കോട്ടൺ സിംഗിൾ ജേഴ്സി: *AED 12.50 / KG മുതൽ*\n"
                            "• പ്രീമിയം ഡെനിം റോൾസ്: *AED 8.50 / Yard മുതൽ*\n"
                            "• പോളിസ്റ്റർ തുണിത്തരങ്ങൾ: *AED 6.50 / Yard മുതൽ*\n\n"
                            "ചിത്രങ്ങൾ കാണാൻ *പുതിയത്* എന്ന് ടൈപ്പ് ചെയ്യുക!"
                        )
                        send_whatsapp_message(from_number, reply)
                    
                    elif user_text in ["സ്ഥലം", "location malayalam"]:
                        send_whatsapp_location(
                            to=from_number,
                            name="Awali International Textile Trading",
                            address="Industrial Area, Dubai, UAE",
                            latitude=25.1972,   
                            longitude=55.2744
                        )
                    
                    elif user_text in ["പുതിയത്", "new malayalam"]:
                        sample_image = "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600&auto=format&fit=crop"
                        caption = "✨ *പുതിയ സ്റ്റോക്ക്: പ്രീമിയം കോട്ടൺ ട്വിൽ റോളുകൾ* ✨\n\n• GSM: 220\n• വീതി: 58/60 ഇഞ്ച്\n• വില: *AED 14.50 / Meter*\n• സ്റ്റോക്ക്: ദുബായ് വെയർഹൗസിൽ ലഭ്യമാണ്."
                        send_whatsapp_image(from_number, sample_image, caption)
                    
                    elif user_text == "ഏജന്റ്":
                        reply = "🤝 *സെയിൽസ് ടീമുമായി ബന്ധിപ്പിക്കുന്നു...* ഞങ്ങളുടെ ബിസിനസ് ഏജന്റ് ഉടൻ നിങ്ങളെ ബന്ധപ്പെടും."
                        send_whatsapp_message(from_number, reply)

                # ====================================================
                # D. DEFAULT MENU (නොදන්නා වචනයක් ආවොත් භාෂා 3ම පෙන්වයි)
                # ====================================================
                else:
                    reply = (
                        "Welcome to Awali Textiles! 🌐\n"
                        "• For English reply: *Hi*\n"
                        "• हिंदी के लिए रिप्लाई करें: *नमस्ते*\n"
                        "• മലയാളത്തിനായി ടൈപ്പ് ചെയ്യുക: *ഹലോ*"
                    )
                    send_whatsapp_message(from_number, reply)
            
    except Exception as e:
        print("Error:", e)
        
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(port=10000)

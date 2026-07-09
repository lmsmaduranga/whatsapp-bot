import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = "MySecretToken123"

# ⚠️ ඔයාගේ Token එක සහ ලොග්ස් එකෙන් අහුවුණු අලුත්ම නිවැරදිම Phone Number ID එක මෙතන තියෙන්නේ
ACCESS_TOKEN = r"EAAUx74tjPN8BRznZBFdCLalPQvOZA6qu80QwS0XYnnFAZB6FZAB013cXIMj4r9eCReXdPZBByUuUHvnPw4bw0gKNFfB41tUrnwVWepc6F7af3BCFScok6jHoChPkpQCZADjSbnyBeQ5EtifUq600ZCU0uoWtAzL90R00lpI8qF8H1Kttu19KocJPeItWAx2s1aozg3RoXfB7mAcmXYakGegb3uMdZCO8y7Y2ZBfeIxZCgFeA4ZCCyJIz4kSp7k5poZC8ZBnR3dtMcbblZCliXRxF1ZCJmAmrjsQ"
PHONE_NUMBER_ID = "1272291502626274"

# 1. 💬 සාමාන්‍ย Text මැසේජ් යවන ක්‍රමය
def send_whatsapp_message(to, text):
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"
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

# 2. 📍 GOOGLE MAP LOCATION එක මැප් කාඩ් එකක් විදිහටම යවන ක්‍රමය (Al Quoz, Dubai Coordinates)
def send_whatsapp_location(to, name, address, latitude=25.1224, longitude=55.2012):
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"
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
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"
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
            # 🎙️ VOICE NOTE / AUDIO එකක් ආවොත් සිදුවන ක්‍රියාවලිය
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
            # 💬 TEXT මැසේජ් ආවොත් සිදුවන ක්‍රියාවලිය
            # ----------------------------------------------------
            elif msg_type == "text":
                user_text = message["text"]["body"].lower().strip()
                
                # ====================================================
                # A. ENGLISH B2B LOGIC
                # ====================================================
                if any(word in user_text for word in ["hi", "hello", "price", "stock", "available", "deliver", "delivery", "quotation", "location", "address", "new", "material", "hours", "working", "agent"]):
                    
                    if user_text in ["hi", "hello"]:
                        reply = "Welcome to *Awali International Textile Trading*! 🌐🧵 How can we assist your business today? (You can type your questions in English, Hindi, or Malayalam)"
                        send_whatsapp_message(from_number, reply)
                    
                    elif "stock" in user_text or "available" in user_text:
                        reply = "Thank you for your inquiry. Please share the product name or item code, and we will check the availability for you as soon as possible."
                        send_whatsapp_message(from_number, reply)
                        
                    elif "price" in user_text:
                        reply = "Thank you for your interest. Please let us know the product you are referring to, and we will provide the latest price and availability."
                        send_whatsapp_message(from_number, reply)
                        
                    elif "deliver" in user_text or "delivery" in user_text:
                        reply = "Thank you for your inquiry. Delivery time depends on your location and product availability. Please share your delivery location, and we'll provide an estimated delivery schedule."
                        send_whatsapp_message(from_number, reply)
                        
                    elif "quotation" in user_text:
                        reply = "Certainly. Please send us the product details, required quantity, and your company information. We will prepare and send you a quotation as soon as possible."
                        send_whatsapp_message(from_number, reply)
                        
                    elif user_text in ["location", "address"]:
                        send_whatsapp_location(from_number, "Awali International Textile Trading", "Al Quoz Industrial Area, Dubai, UAE")
                        reply = "Thank you for your inquiry. Above is our exact location and Google Maps link. Please let us know which branch you are looking for if you need further details."
                        send_whatsapp_message(from_number, reply)
                        
                    elif "new" in user_text or "material" in user_text:
                        sample_image = "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600&auto=format&fit=crop"
                        caption = "Thank you for your interest. We regularly receive new stock. Please let us know which product category you are looking for, and we'll share our latest arrivals and available options."
                        send_whatsapp_image(from_number, sample_image, caption)
                        
                    elif "hours" in user_text or "working" in user_text:
                        reply = "Thank you for contacting us. Please let us know which branch you are referring to, and we'll share the working hours. (Standard Dubai Office: 9:00 AM - 6:00 PM)"
                        send_whatsapp_message(from_number, reply)
                        
                    elif user_text == "agent":
                        reply = "🤝 *Connecting to Export Team...* One of our B2B trade specialists will text you back shortly."
                        send_whatsapp_message(from_number, reply)

                # ====================================================
                # B. HINDI B2B LOGIC (हिंदी)
                # ====================================================
                elif any(word in user_text for word in ["नमस्ते", "namaste", "दाम", "रेट", "स्टॉक", "उपलब्ध", "डिलीवरी", "कोटेशन", "पता", "लोकेशन", "नया", "समय", "एजेंट"]):
                    
                    if user_text in ["नमस्ते", "namaste"]:
                        reply = "*अवाली इंटरनेशनल टेक्सटाइल ट्रेडिंग* में आपका स्वागत है! 🌐🧵 आज हम आपके बिजनेस की क्या मदद कर सकते हैं?"
                        send_whatsapp_message(from_number, reply)
                    
                    elif "स्टॉक" in user_text or "उपलब्ध" in user_text:
                        reply = "पूछताछ के लिए धन्यवाद। कृपया प्रोडक्ट का नाम या आइटम कोड साझा करें, और हम जल्द से जल्द आपके लिए उपलब्धता की जांच करेंगे।"
                        send_whatsapp_message(from_number, reply)
                        
                    elif "दाम" in user_text or "रेट" in user_text:
                        reply = "आपकी रुचि के लिए धन्यवाद। कृपया हमें बताएं कि आप किस प्रोडक्ट के बारे में बात कर रहे हैं, और हम आपको नवीनतम कीमत प्रदान करेंगे।"
                        send_whatsapp_message(from_number, reply)
                        
                    elif "डिलीवरी" in user_text:
                        reply = "पूछताछ के लिए धन्यवाद। डिलीवरी का समय आपकी लोकेशन और प्रोडक्ट की उपलब्धता पर निर्भर करता. कृपया अपनी डिलीवरी लोकेशन साझा करें।"
                        send_whatsapp_message(from_number, reply)
                        
                    elif "कोटेशन" in user_text:
                        reply = "बिल्कुल। कृपया हमें प्रोडक्ट का विवरण, आवश्यक मात्रा और अपनी कंपनी की जानकारी भेजें। हम जल्द से जल्द कोटेशन तैयार करेंगे।"
                        send_whatsapp_message(from_number, reply)
                        
                    elif "पता" in user_text or "लोकेशन" in user_text:
                        send_whatsapp_location(from_number, "Awali International Textile Trading", "Al Quoz Industrial Area, Dubai, UAE")
                        reply = "पूछताछ के लिए धन्यवाद। ऊपर हमारा सटीक स्थान और गूगल मैप्स लिंक है। कृपया हमें बताएं कि आप किस ब्रांच को ढूंढ रहे हैं।"
                        send_whatsapp_message(from_number, reply)
                        
                    elif "नया" in user_text:
                        sample_image = "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600&auto=format&fit=crop"
                        caption = "आपकी रुचि के लिए धन्यवाद। हमें नियमित रूप से नया स्टॉक मिलता है। कृपया हमें बताएं कि आप किस प्रोडक्ट केटेगरी की तलाश कर रहे हैं।"
                        send_whatsapp_image(from_number, sample_image, caption)
                        
                    elif "समय" in user_text:
                        reply = "हमसे संपर्क करने के लिए धन्यवाद। कृपया हमें बताएं कि आप किस ब्रांच की बात कर रहे हैं, और हम वर्किंग ऑवर्स साझा करेंगे।"
                        send_whatsapp_message(from_number, reply)
                        
                    elif user_text == "एजेंट":
                        reply = "🤝 *एक्सपोर्ट टीम से जुड़ रहे हैं...* हमारे बी2बी सेल्स एजेंट कुछ ही मिनटों में आपसे संपर्क करेंगे।"
                        send_whatsapp_message(from_number, reply)

                # ====================================================
                # C. MALAYALAM B2B LOGIC (മലയാളം)
                # ====================================================
                elif any(word in user_text for word in ["ഹലോ", "നമസ്കാരം", "വില", "സ്റ്റോക്ക്", "ലഭ്യമാണോ", "ഡെലിവറി", "കൊട്ടേഷൻ", "സ്ഥലം", "ലൊക്കേഷൻ", "പുതിയത്", "സമയം", "ഏജന്റ്"]):
                    
                    if user_text in ["ഹലോ", "നമസ്കാരം"]:
                        reply = "അവാലി ഇന്റർനാഷണൽ ടെക്സ്റ്റൈൽ ട്രേഡിംഗിലേക്ക് സ്വാഗതം! 🌐🧵 ഇന്ന് ഞങ്ങൾ നിങ്ങൾക്ക് എങ്ങനെയാണ് സഹായിക്കേണ്ടത്?"
                        send_whatsapp_message(from_number, reply)
                    
                    elif "സ്റ്റോക്ക്" in user_text or "ലഭ്യമാണോ" in user_text:
                        reply = "നിങ്ങളുടെ അന്വേഷണത്തിന് നന്ദി. ദയവായി ഉൽപ്പന്നത്തിന്റെ പേരോ ഐറ്റം കോഡോ പങ്കുവെക്കുക, ഞങ്ങൾ ലഭ്യത എത്രയും വേഗം പരിശോധിക്കാം."
                        send_whatsapp_message(from_number, reply)
                        
                    elif "വില" in user_text:
                        reply = "താൽപ്പനത്തിന് നന്ദി. നിങ്ങൾ ഉദ്ദേശിക്കുന്ന ഉൽപ്പന്നം ഏതാണെന്ന് ഞങ്ങളെ അറിയിക്കുക, ഞങ്ങൾ പുതിയ വിലവിവരങ്ങൾ നൽകാം."
                        send_whatsapp_message(from_number, reply)
                        
                    elif "ഡെലിവറി" in user_text:
                        reply = "അന്വേഷണത്തിന് നന്ദി. ഡെലിവറി സമയം നിങ്ങളുടെ ലൊക്കേഷനെയും ഉൽപ്പന്നത്തിന്റെ ലഭ്യതയെയും ആശ്രയിച്ചിരിക്കുന്നു. ദയവായി നിങ്ങളുടെ ലൊക്കേഷൻ പങ്കുവെക്കുക."
                        send_whatsapp_message(from_number, reply)
                        
                    elif "കൊട്ടേഷൻ" in user_text:
                        reply = "തീർച്ചയായും. ദയവായി ഉൽപ്പന്ന വിവരങ്ങളും ആവശ്യമായ അളവും നിങ്ങളുടെ കമ്പനിയുടെ വിവരങ്ങളും ഞങ്ങൾക്ക് അയച്ചുതരുക. ഞങ്ങൾ കൊട്ടേഷൻ തയ്യാറാക്കാം."
                        send_whatsapp_message(from_number, reply)
                        
                    elif "സ്ഥലം" in user_text or "ലൊക്കേഷൻ" in user_text:
                        send_whatsapp_location(from_number, "Awali International Textile Trading", "Al Quoz Industrial Area, Dubai, UAE")
                        reply = "അന്വേഷണത്തിന് നന്ദി. മുകളിൽ ഞങ്ങളുടെ കൃത്യമായ ലൊക്കേഷനും ഗൂഗിൾ മാപ്പ് ലിങ്കും നൽകിയിട്ടുണ്ട്. നിങ്ങൾക്ക് ഏത് ബ്രാഞ്ചിന്റെ വിവരങ്ങളാണ് വേണ്ടതെന്ന് അറിയിക്കുക."
                        send_whatsapp_message(from_number, reply)
                        
                    elif "പുതിയത്" in user_text:
                        sample_image = "https://images.unsplash.com/photo-1544816155-12df9643f363?q=80&w=600&auto=format&fit=crop"
                        caption = "താൽപ്പര്യത്തിന് നന്ദി. ഞങ്ങൾക്ക് സ്ഥിരമായി പുതിയ സ്റ്റോക്കുകൾ വരാറുണ്ട്. നിങ്ങൾ ഏത് തരം തുണിത്തരങ്ങളാണ് നോക്കുന്നതെന്ന് അറിയിക്കുക."
                        send_whatsapp_image(from_number, sample_image, caption)
                        
                    elif "സമയം" in user_text:
                        reply = "ഞങ്ങളെ ബന്ധപ്പെട്ടതിന് നന്ദി. നിങ്ങൾ ഏത് ബ്രാഞ്ചിനെക്കുറിച്ചാണ് ചോദിക്കുന്നതെന്ന് അറിയിക്കുക, ഞങ്ങൾ ഓഫീസ് സമയം പങ്കുവെക്കാം."
                        send_whatsapp_message(from_number, reply)
                        
                    elif user_text == "ഏജന്റ്":
                        reply = "🤝 *സെയിൽസ് ടീമുവായി ബന്ധിപ്പിക്കുന്നു...* ഞങ്ങളുടെ ബിസിനസ് ഏജന്റ് ഉടൻ നിങ്ങളെ ബന്ധപ്പെടും."
                        send_whatsapp_message(from_number, reply)

                # ====================================================
                # D. DEFAULT REPLY
                # ====================================================
                else:
                    reply = "Welcome to Awali International Textile Trading! 🌐 How can we help you today? (English / Hindi / Malayalam)"
                    send_whatsapp_message(from_number, reply)
            
    except Exception as e:
        print("Error:", e)
        
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
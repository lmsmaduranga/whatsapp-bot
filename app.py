import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import base64
import json

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "MySecretToken123")
ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

print("========== APP STARTED ==========")

# ==============================================================================
# MULTILINGUAL MENUS
# ==============================================================================

WELCOME_MESSAGE = (
    "👋 Welcome to Al Awali Trading Co. LLC.\n\n"
    "To continue, please select your preferred language:\n"
    "🇬🇧 A. English\n"
    "🇦🇪 B. العربية (Arabic)\n"
    "🇮🇳 C. हिन्दी / اردو (Hindi / Urdu)\n"
    "🇷🇺 D. Русский (Russian)"
)

MAIN_MENU_EN = (
    "How can we assist you today?\n\n"
    "1️⃣ Browse Fabric Collections\n"
    "2️⃣ Request a Fabric Quotation\n"
    "3️⃣ Wholesale / Bulk Order Inquiry\n"
    "4️⃣ Check Product Availability\n"
    "5️⃣ Send Fabric Sample / Reference Image 📸\n"
    "6️⃣ Delivery & Shipping Information\n"
    "7️⃣ Our Location 📍\n"
    "8️⃣ Contact Our Sales Team\n\n"
    "9️⃣ Back to Language Menu\n\n"
    "💬 Or just type your question!"
)

# ==============================================================================
# UPDATED ANSWER 5 - Fabric Sample (With Image Instructions)
# ==============================================================================

ANSWER_SAMPLE_EN = """📸 *Send Fabric Sample / Reference Image*

Take a clear photo of the fabric you need and send it to us!

📷 *Tips for a good photo:*
• Use natural daylight
• Show the texture clearly
• Include size reference (coin, ruler)
• Capture the actual color

📤 *How to send:*
• Tap the 📎 attachment icon
• Select 📷 Camera or 🖼️ Gallery
• Choose your fabric photo
• Send it

Our team will:
1️⃣ Identify the fabric type
2️⃣ Check availability in stock
3️⃣ Provide specs and pricing

📞 +971 4 123 4567

*Send your fabric photo now!*"""

ANSWER_SAMPLE_AR = """📸 *إرسال عينة قماش / صورة مرجعية*

التقط صورة واضحة للقماش الذي تحتاجه وأرسلها إلينا!

📷 *نصائح لصورة جيدة:*
• استخدم ضوء النهار الطبيعي
• أظهر الملمس بوضوح
• قم بتضمين مرجع للحجم (عملة، مسطرة)
• التقط اللون الفعلي

📤 *كيفية الإرسال:*
• اضغط على أيقونة المرفقات 📎
• اختر الكاميرا 📷 أو المعرض 🖼️
• اختر صورة القماش
• أرسلها

سيتولى فريقنا:
1️⃣ تحديد نوع القماش
2️⃣ التحقق من التوفر في المخزون
3️⃣ تقديم المواصفات والأسعار

📞 +971 4 123 4567

*أرسل صورة القماش الآن!*"""

ANSWER_SAMPLE_HI = """📸 *फैब्रिक सैंपल / संदर्भ छवि भेजें*

आपको जिस कपड़े की ज़रूरत है उसकी स्पष्ट फोटो लें और हमें भेजें!

📷 *अच्छी फोटो के लिए टिप्स:*
• प्राकृतिक दिन के उजाले का उपयोग करें
• बनावट को स्पष्ट रूप से दिखाएं
• आकार संदर्भ शामिल करें (सिक्का, रूलर)
• वास्तविक रंग कैप्चर करें

📤 *कैसे भेजें:*
• 📎 अटैचमेंट आइकन टैप करें
• 📷 कैमरा या 🖼️ गैलरी चुनें
• अपनी फैब्रिक फोटो चुनें
• भेजें

हमारी टीम:
1️⃣ फैब्रिक प्रकार की पहचान करेगी
2️⃣ स्टॉक में उपलब्धता जांचेगी
3️⃣ स्पेक्स और कीमत प्रदान करेगी

📞 +971 4 123 4567

*अब अपनी फैब्रिक फोटो भेजें!*"""

ANSWER_SAMPLE_RU = """📸 *Отправить образец ткани / изображение*

Сделайте четкое фото ткани, которая вам нужна, и отправьте его нам!

📷 *Советы для хорошего фото:*
• Используйте естественный дневной свет
• Покажите текстуру четко
• Включите ссылку на размер (монета, линейка)
• Захватите реальный цвет

📤 *Как отправить:*
• Нажмите на значок вложения 📎
• Выберите 📷 Камера или 🖼️ Галерея
• Выберите фото ткани
• Отправьте

Наша команда:
1️⃣ Определит тип ткани
2️⃣ Проверит наличие на складе
3️⃣ Предоставит спецификации и цены

📞 +971 4 123 4567

*Отправьте фото ткани сейчас!*"""

# ==============================================================================
# OTHER ANSWERS (Short versions)
# ==============================================================================

ANSWER_QUOTATION_EN = """📋 *Fabric Quotation Request*

Please share:
• Fabric type and specifications
• Quantity required (MOQ: 1 pallet)
• Quality grade
• Delivery location

📞 +971 4 123 4567"""

ANSWER_WHOLESALE_EN = """📦 *Wholesale & Bulk Orders*

MOQ: 1 Pallet (500-1000 meters)
✓ Competitive pricing
✓ Global shipping
✓ Flexible payment terms

📞 +971 4 123 4567"""

ANSWER_AVAILABILITY_EN = """✅ *Product Availability*

Current stock:
• Abaya Fabrics - ✅ In Stock
• Cotton Fabrics - ✅ In Stock
• Linen Fabrics - ✅ In Stock
• Silk Fabrics - ⚠️ Limited

📞 +971 4 123 4567"""

ANSWER_DELIVERY_EN = """🚚 *Delivery & Shipping*

Sea: 2-4 weeks
Air: 3-7 days
Land (GCC): 5-7 days

📞 +971 4 123 4567"""

ANSWER_LOCATION_EN = """📍 *Our Location*

Al Awali Trading Co LLC
Al Sabkha, Deira, Dubai, UAE

Sun-Thu: 9AM-6PM
Fri: Closed
Sat: 10AM-2PM

📞 +971 4 123 4567"""

ANSWER_CONTACT_EN = """📞 *Contact Us*

Phone: +971 4 123 4567
WhatsApp: +971 54 218 0677
Email: sales@alawalitrading.com

📍 Al Sabkha, Deira, Dubai, UAE"""

# ==============================================================================
# LANGUAGE MAPS
# ==============================================================================

SAMPLE_RESPONSES = {
    'en': ANSWER_SAMPLE_EN,
    'ar': ANSWER_SAMPLE_AR,
    'hi': ANSWER_SAMPLE_HI,
    'ru': ANSWER_SAMPLE_RU
}

# ==============================================================================
# CORE FUNCTIONS
# ==============================================================================

def download_whatsapp_image(media_id):
    """Download image from WhatsApp using media ID"""
    if not ACCESS_TOKEN:
        return None
    
    url = f"https://graph.facebook.com/v20.0/{media_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    
    try:
        # Get media URL
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if "url" not in data:
            return None
        
        # Download image
        img_response = requests.get(data["url"], headers=headers)
        return img_response.content
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

def analyze_image_with_gemini(image_bytes, user_text=""):
    """Send image to Gemini for analysis"""
    if not GEMINI_API_KEY:
        return "Thank you for sharing the image. Our team will review it shortly."
    
    # Convert image to base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""
You are an expert fabric/trade manager at Al Awali Trading Co LLC.

The user sent a fabric image. Please analyze it and provide:
1. What type of fabric this appears to be (cotton, silk, linen, etc.)
2. Quality assessment
3. Possible uses
4. Recommendations

User also said: {user_text if user_text else "No additional text"}

Keep response short, professional (3-4 sentences), and include our contact: +971 4 123 4567
"""
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {"inline_data": {"mime_type": "image/jpeg", "data": base64_image}}
            ]
        }]
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=60)
        data = response.json()
        
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        return "Thank you for the fabric image. Our team will review it and get back to you shortly."
    except Exception as e:
        print(f"Gemini vision error: {e}")
        return "Thank you for sharing the image. Our team will analyze it and provide details shortly."

def send_whatsapp_message(to, text):
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        return False
    
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def send_location(to):
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        return False
    
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp", "to": to, "type": "location",
        "location": {
            "latitude": 25.2694, "longitude": 55.3023,
            "name": "Al Awali Trading Co LLC Head Office",
            "address": "Al Sabkha, Deira, Dubai, UAE"
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"
        }, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Location error: {e}")
        return False

# ==============================================================================
# USER STATE MANAGEMENT
# ==============================================================================

user_states = {}

def get_user_state(user_id):
    return user_states.get(user_id, {"menu": "welcome", "lang": "en"})

def set_user_state(user_id, state):
    user_states[user_id] = state

# ==============================================================================
# WEBHOOK
# ==============================================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running", "service": "Al Awali WhatsApp Bot", "version": "7.0.0"}), 200

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("📨 Webhook received")
        
        value = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
        if "messages" not in value:
            return jsonify({"status": "ignored"}), 200

        message = value["messages"][0]
        sender = message["from"]
        msg_type = message["type"]

        user_state = get_user_state(sender)
        current_menu = user_state.get("menu", "welcome")
        lang = user_state.get("lang", "en")

        # ================================================================
        # IMAGE MESSAGE HANDLING (NEW - Advanced)
        # ================================================================
        if msg_type == "image":
            print(f"📸 Image received from {sender}")
            
            # Get image details
            image_data = message.get("image", {})
            media_id = image_data.get("id")
            caption = message.get("text", {}).get("body", "") if "text" in message else ""
            
            # Download image
            image_bytes = download_whatsapp_image(media_id)
            
            if image_bytes:
                # Analyze with Gemini Vision
                analysis = analyze_image_with_gemini(image_bytes, caption)
                
                # Send response
                analysis_msg = f"📸 *Fabric Analysis*\n\n{analysis}"
                send_whatsapp_message(sender, analysis_msg)
                
                # Send follow-up
                followup = {
                    'en': "🔄 To proceed, please tell us:\n• Quantity needed (MOQ: 1 pallet)\n• Preferred color/variety\n\n📞 +971 4 123 4567",
                    'ar': "🔄 للمتابعة، يرجى إخبارنا:\n• الكمية المطلوبة (الحد الأدنى: 1 باليت)\n• اللون/النوع المفضل\n\n📞 +971 4 123 4567",
                    'hi': "🔄 आगे बढ़ने के लिए, कृपया बताएं:\n• आवश्यक मात्रा (MOQ: 1 पैलेट)\n• पसंदीदा रंग/विविधता\n\n📞 +971 4 123 4567",
                    'ru': "🔄 Чтобы продолжить, пожалуйста, сообщите:\n• Необходимое количество (MOQ: 1 паллета)\n• Предпочтительный цвет\n\n📞 +971 4 123 4567"
                }
                send_whatsapp_message(sender, followup.get(lang, followup['en']))
            else:
                # Fallback if image can't be downloaded
                fallback = {
                    'en': "📸 Thank you for sharing the image! Our team will review it and provide details within 2 hours. 📞 +971 4 123 4567",
                    'ar': "📸 شكراً لمشاركة الصورة! سيقوم فريقنا بمراجعتها وتقديم التفاصيل خلال ساعتين. 📞 +971 4 123 4567",
                    'hi': "📸 छवि साझा करने के लिए धन्यवाद! हमारी टीम 2 घंटे के भीतर समीक्षा करेगी। 📞 +971 4 123 4567",
                    'ru': "📸 Спасибо за фото! Наша команда рассмотрит его в течение 2 часов. 📞 +971 4 123 4567"
                }
                send_whatsapp_message(sender, fallback.get(lang, fallback['en']))
            
            set_user_state(sender, {"menu": "main", "lang": lang})
            return jsonify({"status": "success"}), 200

        # ================================================================
        # TEXT MESSAGE HANDLING
        # ================================================================
        if msg_type == "text":
            user_text = message["text"]["body"].strip()
            clean_text = user_text.lower()
            clean_num = clean_text.replace(".", "")

            print(f"👤 User: {sender}")
            print(f"💬 Text: {user_text}")
            print(f"📋 Menu: {current_menu}")
            print(f"🌐 Language: {lang}")

            # --- GREETINGS ---
            greeting_keywords = ["hi", "hello", "hey", "salam", "assalamualaikum",
                               "привет", "مرحبا", "नमस्ते"]
            
            if any(greeting in clean_text for greeting in greeting_keywords):
                send_whatsapp_message(sender, WELCOME_MESSAGE)
                set_user_state(sender, {"menu": "welcome", "lang": "en"})
                return jsonify({"status": "success"}), 200

            # --- LANGUAGE SELECTION ---
            if clean_num in ["a", "а"]:
                send_whatsapp_message(sender, MAIN_MENU_EN)
                set_user_state(sender, {"menu": "main", "lang": "en"})
                return jsonify({"status": "success"}), 200
            elif clean_num == "b":
                send_whatsapp_message(sender, MAIN_MENU_AR)  # You'll need to add Arabic main menu
                set_user_state(sender, {"menu": "main", "lang": "ar"})
                return jsonify({"status": "success"}), 200
            elif clean_num == "c":
                send_whatsapp_message(sender, MAIN_MENU_HI)  # You'll need to add Hindi main menu
                set_user_state(sender, {"menu": "main", "lang": "hi"})
                return jsonify({"status": "success"}), 200
            elif clean_num == "d":
                send_whatsapp_message(sender, MAIN_MENU_RU)  # You'll need to add Russian main menu
                set_user_state(sender, {"menu": "main", "lang": "ru"})
                return jsonify({"status": "success"}), 200

            # --- MAIN MENU (1-9) ---
            if current_menu == "main":
                if clean_num == "1":
                    # Fabric menu
                    send_whatsapp_message(sender, FABRIC_MENU_EN)  # Add fabric menu
                    set_user_state(sender, {"menu": "fabric_categories", "lang": lang})
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "2":
                    send_whatsapp_message(sender, ANSWER_QUOTATION_EN)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "3":
                    send_whatsapp_message(sender, ANSWER_WHOLESALE_EN)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "4":
                    send_whatsapp_message(sender, ANSWER_AVAILABILITY_EN)
                    return jsonify({"status": "success"}), 200
                
                # ⭐ UPDATED: Option 5 - Send Fabric Sample
                elif clean_num == "5":
                    # Send sample instruction in user's language
                    response = SAMPLE_RESPONSES.get(lang, ANSWER_SAMPLE_EN)
                    send_whatsapp_message(sender, response)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "6":
                    send_whatsapp_message(sender, ANSWER_DELIVERY_EN)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "7":
                    send_location(sender)
                    send_whatsapp_message(sender, ANSWER_LOCATION_EN)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "8":
                    send_whatsapp_message(sender, ANSWER_CONTACT_EN)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "9":
                    send_whatsapp_message(sender, WELCOME_MESSAGE)
                    set_user_state(sender, {"menu": "welcome", "lang": "en"})
                    return jsonify({"status": "success"}), 200

            # --- FABRIC CATEGORIES ---
            elif current_menu == "fabric_categories":
                if clean_num in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    fabric_names = {
                        "1": "Abaya & Black Fabrics",
                        "2": "Dress & Fashion Fabrics",
                        "3": "Cotton Fabrics",
                        "4": "Linen Fabrics",
                        "5": "Silk Fabrics",
                        "6": "Embroidery & Designer Fabrics",
                        "7": "Suiting Fabrics",
                        "8": "Other Fabrics"
                    }
                    send_whatsapp_message(sender, f"🧵 *{fabric_names[clean_num]}*\n\nPremium wholesale fabrics available. MOQ: 1 pallet.\n📞 +971 4 123 4567")
                    return jsonify({"status": "success"}), 200
                elif clean_num == "0":
                    send_whatsapp_message(sender, MAIN_MENU_EN)
                    set_user_state(sender, {"menu": "main", "lang": lang})
                    return jsonify({"status": "success"}), 200

        # --- OTHER MESSAGE TYPES ---
        else:
            send_whatsapp_message(sender, "📞 +971 4 123 4567")

    except Exception as e:
        print(f"❌ WEBHOOK ERROR: {str(e)}")
        try:
            if sender:
                send_whatsapp_message(sender, "Error occurred. Please try again. 📞 +971 4 123 4567")
        except:
            pass

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

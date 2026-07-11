import os
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "MySecretToken123")
ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

print("========== APP STARTED ==========")
print("ACCESS TOKEN:", "OK" if ACCESS_TOKEN else "MISSING")
print("PHONE NUMBER ID:", PHONE_NUMBER_ID if PHONE_NUMBER_ID else "MISSING")
print("GEMINI KEY:", "OK" if GEMINI_API_KEY else "MISSING")

# ==============================================================================
# SYSTEM INSTRUCTION FOR GEMINI
# ==============================================================================

system_instruction = """
You are the expert B2B Export Trade Manager for Al Awali Trading Co LLC Head Office based in Dubai, UAE.
We import premium fabric rolls globally and export wholesale fabric supplies to GCC countries and worldwide.

CRITICAL RULES:
1. Always respond in the SAME LANGUAGE as the customer's question (English, Arabic, Hindi, or Russian)
2. Keep replies short, professional, and business-focused (2-4 sentences maximum)
3. We ONLY sell wholesale fabric rolls/bales. MOQ is 1 pallet or container
4. We do NOT sell small retail quantities
5. Always include our contact: +971 4 123 4567 or sales@alawalitrading.com
6. Be helpful and polite
7. If you don't know something, direct them to our sales team

COMPANY INFO:
- Name: Al Awali Trading Co LLC
- Location: Al Sabkha, Deira, Dubai, UAE
- Business: Premium fabric wholesale trading
- Products: Abaya fabrics, fashion fabrics, cotton, linen, silk, embroidered fabrics
- Services: Global shipping, bulk orders, custom sourcing

RESPONSE STYLE:
- Professional but friendly
- Focus on B2B wholesale
- Short and to the point
- Always offer to help with more details
"""

# ==============================================================================
# MULTILINGUAL MENUS
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
    "9️⃣ Back to Language Menu\n\n"
    "💬 Or just type your question and I'll help!"
)

MAIN_MENU_AR = (
    "كيف يمكننا مساعدتك اليوم؟\n\n"
    "1️⃣ تصفح مجموعات الأقمشة\n"
    "2️⃣ طلب عرض سعر للأقمشة\n"
    "3️⃣ استفسار عن طلبات الجملة\n"
    "4️⃣ التحقق من توفر المنتج\n"
    "5️⃣ إرسال عينة قماش\n"
    "6️⃣ معلومات التوصيل والشحن\n"
    "7️⃣ موقعنا 📍\n"
    "8️⃣ الاتصال بفريق المبيعات\n\n"
    "9️⃣ العودة إلى قائمة اللغة\n\n"
    "💬 أو اكتب سؤالك مباشرة!"
)

MAIN_MENU_HI = (
    "आज हम आपकी क्या सहायता कर सकते हैं?\n\n"
    "1️⃣ फैब्रिक कलेक्शन देखें\n"
    "2️⃣ फैब्रिक कोटेशन के लिए अनुरोध करें\n"
    "3️⃣ थोक / बल्क ऑर्डर पूछताछ\n"
    "4️⃣ उत्पाद की उपलब्धता जांचें\n"
    "5️⃣ फैब्रिक सैंपल भेजें\n"
    "6️⃣ डिलीवरी और शिपिंग की जानकारी\n"
    "7️⃣ हमारा स्थान 📍\n"
    "8️⃣ हमारी बिक्री टीम से संपर्क करें\n\n"
    "9️⃣ भाषा मेनू पर वापस जाएं\n\n"
    "💬 या सीधे अपना प्रश्न टाइप करें!"
)

MAIN_MENU_RU = (
    "Как мы можем помочь вам сегодня?\n\n"
    "1️⃣ Посмотреть коллекции тканей\n"
    "2️⃣ Запросить прайс-лист\n"
    "3️⃣ Оптовые закупки\n"
    "4️⃣ Проверить наличие товара\n"
    "5️⃣ Отправить образец ткани\n"
    "6️⃣ Информация о доставке\n"
    "7️⃣ Наше местоположение 📍\n"
    "8️⃣ Связаться с отделом продаж\n\n"
    "9️⃣ Вернуться к выбору языка\n\n"
    "💬 Или задайте свой вопрос напрямую!"
)

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
    "💬 Or describe what you're looking for!"
)

# ==============================================================================
# FABRIC DETAILS (Pre-defined responses for menu options)
# ==============================================================================

FABRIC_RESPONSES = {
    "1": "🧵 *Abaya & Black Fabrics*\n\nPremium abaya fabrics including crepe, nidha, and jersey.\nAvailable in black, navy, and dark shades.\nMOQ: 1 pallet.\n\nContact sales for catalog: +971 4 123 4567",
    
    "2": "👗 *Dress & Fashion Fabrics*\n\nChiffon, georgette, viscose, and printed fabrics.\nLatest designs and colors available.\nMOQ: 1 pallet.\n\nContact sales for collection: +971 4 123 4567",
    
    "3": "🌿 *Cotton Fabrics*\n\n100% cotton in poplin, oxford, twill, and denim.\nIdeal for shirts, dresses, and home textiles.\nMOQ: 1 pallet.\n\nContact sales for samples: +971 4 123 4567",
    
    "4": "🧵 *Linen Fabrics*\n\nPure linen and linen blends.\nBreathable, durable, and elegant.\nAvailable in natural and dyed colors.\nMOQ: 1 pallet.",
    
    "5": "✨ *Silk Fabrics*\n\nLuxury pure silk, silk blends, and satin.\nPerfect for high-end fashion and bridal wear.\nMOQ: 1 pallet.\n\nContact sales for pricing: +971 4 123 4567",
    
    "6": "🎨 *Embroidery & Designer Fabrics*\n\nExclusive embroidered and designer fabrics.\nHandwork, machine embroidery, and digital prints.\nCustom designs available.\nMOQ: 1 pallet.",
    
    "7": "👔 *Suiting Fabrics*\n\nPremium suiting for men and women.\nWool blends, polyester blends, and stretch fabrics.\nSolid, checks, and stripes available.\nMOQ: 1 pallet.",
    
    "8": "📦 *Other Fabrics*\n\nSpecialized technical textiles and industrial fabrics.\nCustom orders available.\nContact our team for specific requirements.\n+971 4 123 4567"
}

# ==============================================================================
# CORE FUNCTIONS
# ==============================================================================

def get_gemini_response(message):
    """Get response from Gemini API for free-text questions"""
    if not GEMINI_API_KEY:
        return "Thank you for your question. For detailed assistance, please contact our sales team at +971 4 123 4567 or email sales@alawalitrading.com"
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": message}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        data = response.json()
        print("Gemini Response:", data)  # Debug log
        
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Thank you for contacting Al Awali Trading Co LLC. Our team will assist you shortly. Call +971 4 123 4567"
            
    except requests.exceptions.Timeout:
        print("Gemini API Timeout")
        return "We're experiencing high volume. Please contact our sales team directly at +971 4 123 4567 for immediate assistance."
    except Exception as e:
        print("Gemini Error:", str(e))
        return "Thank you for your question. Our team will respond shortly. Contact: +971 4 123 4567"

def send_whatsapp_message(to, text):
    """Send WhatsApp message"""
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("WhatsApp credentials missing")
        return False
    
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": text}}
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Message sent to {to}")
            return True
        else:
            print(f"Failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

def send_location(to):
    """Send location card"""
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        return False
    
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp", "to": to, "type": "location",
        "location": {
            "latitude": 25.2694, "longitude": 55.3023,
            "name": "Al Awali Trading Co LLC Head Office",
            "address": "Al Sabkha, Deira, Dubai, United Arab Emirates"
        }
    }
    
    try:
        response = requests.post(url, json=payload, headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"
        }, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Location error: {str(e)}")
        return False

# ==============================================================================
# USER STATE MANAGEMENT
# ==============================================================================

user_states = {}

def get_user_state(user_id):
    return user_states.get(user_id, {"menu": "welcome", "language": "en"})

def set_user_state(user_id, state):
    user_states[user_id] = state

# ==============================================================================
# WEBHOOK
# ==============================================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running", 
        "service": "Al Awali WhatsApp Bot",
        "version": "3.0.0",
        "gemini": "enabled" if GEMINI_API_KEY else "disabled"
    }), 200

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        print("Webhook received:", data)
        
        value = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
        if "messages" not in value:
            return jsonify({"status": "ignored"}), 200

        message = value["messages"][0]
        sender = message["from"]
        msg_type = message["type"]

        user_state = get_user_state(sender)
        current_menu = user_state.get("menu", "welcome")

        # ================================================================
        # TEXT MESSAGE HANDLING
        # ================================================================
        if msg_type == "text":
            user_text = message["text"]["body"].strip()
            clean_text = user_text.lower()
            clean_num = clean_text.replace(".", "")

            print(f"User: {sender}, Text: '{user_text}', Menu: {current_menu}")

            # --- STEP 1: Check for Greetings ---
            greeting_keywords = ["hi", "hello", "hey", "salam", "assalamualaikum", 
                               "assalam", "привет", "здравствуйте", "مرحبا", "السلام عليكم", 
                               "नमस्ते", "හලෝ", "ආයුබෝවන්"]
            
            if any(greeting in clean_text for greeting in greeting_keywords):
                send_whatsapp_message(sender, WELCOME_MESSAGE)
                set_user_state(sender, {"menu": "welcome"})
                return jsonify({"status": "success"}), 200

            # --- STEP 2: Check for Language Selection (A, B, C, D) ---
            if clean_num in ["a", "а"]:  # English (also handles Russian 'а')
                send_whatsapp_message(sender, MAIN_MENU_EN)
                set_user_state(sender, {"menu": "main", "language": "en"})
                return jsonify({"status": "success"}), 200
            elif clean_num == "b":
                send_whatsapp_message(sender, MAIN_MENU_AR)
                set_user_state(sender, {"menu": "main", "language": "ar"})
                return jsonify({"status": "success"}), 200
            elif clean_num == "c":
                send_whatsapp_message(sender, MAIN_MENU_HI)
                set_user_state(sender, {"menu": "main", "language": "hi"})
                return jsonify({"status": "success"}), 200
            elif clean_num == "d":
                send_whatsapp_message(sender, MAIN_MENU_RU)
                set_user_state(sender, {"menu": "main", "language": "ru"})
                return jsonify({"status": "success"}), 200

            # --- STEP 3: Check if User is in MAIN MENU ---
            if current_menu == "main":
                # Main Menu Options (1-9)
                if clean_num == "1":  # Fabric Collections
                    send_whatsapp_message(sender, FABRIC_MENU_EN)
                    set_user_state(sender, {"menu": "fabric_categories", "language": "en"})
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "2":  # Quotation
                    send_whatsapp_message(sender, "📋 *Fabric Quotation Request*\n\nTo provide an accurate quote, please specify:\n• Fabric type\n• Quantity (min. 1 pallet)\n• Quality requirements\n• Delivery location\n\nOur team will respond within 24 hours.\n📞 +971 4 123 4567")
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "3":  # Wholesale
                    send_whatsapp_message(sender, "📦 *Wholesale/Bulk Orders*\n\nMOQ: 1 Pallet (500-1000 meters)\nBenefits:\n✓ Competitive pricing\n✓ Flexible payment terms\n✓ Global shipping\n✓ Custom packaging\n\nContact wholesale team: +971 4 123 4567")
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "4":  # Availability
                    send_whatsapp_message(sender, "✅ *Product Availability Check*\n\nTo check availability, please send us:\n• Fabric code or description\n• Required quantity\n• Preferred color/variety\n\nOur team will confirm within 2 hours.\n📞 +971 4 123 4567")
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "5":  # Sample
                    send_whatsapp_message(sender, "📸 *Fabric Sample Request*\n\nPlease send us a photo of the fabric you need, or describe it in detail.\n\nWe'll identify the fabric and provide specifications.\n📞 +971 4 123 4567")
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "6":  # Delivery
                    send_whatsapp_message(sender, "🚚 *Delivery & Shipping*\n\nWorldwide shipping available:\n• Sea Freight: 2-4 weeks\n• Air Freight: 3-7 days\n• Land Transport: GCC 5-7 days\n\nContact for shipping quote: +971 4 123 4567")
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "7":  # Location
                    if send_location(sender):
                        send_whatsapp_message(sender, "📍 Location shared above!\n\nAl Awali Trading Co LLC\nAl Sabkha, Deira, Dubai\nUnited Arab Emirates\n\nVisiting hours: Sun-Thu 9AM-6PM")
                    else:
                        send_whatsapp_message(sender, "📍 Al Awali Trading Co LLC\nAl Sabkha, Deira, Dubai\nUnited Arab Emirates")
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "8":  # Sales Team
                    send_whatsapp_message(sender, "📞 *Contact Our Sales Team*\n\n📱 WhatsApp: +971 54 218 0677\n📞 Phone: +971 4 123 4567\n📧 Email: sales@alawalitrading.com\n🌐 Website: www.alawalitrading.com\n\nWe respond within 24 hours!")
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "9":  # Back to Language
                    send_whatsapp_message(sender, WELCOME_MESSAGE)
                    set_user_state(sender, {"menu": "welcome"})
                    return jsonify({"status": "success"}), 200

            # --- STEP 4: Check if User is in FABRIC CATEGORIES MENU ---
            elif current_menu == "fabric_categories":
                if clean_num in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    # Send pre-defined fabric response
                    response = FABRIC_RESPONSES.get(clean_num, "Fabric details available. Contact sales: +971 4 123 4567")
                    send_whatsapp_message(sender, response)
                    # Stay in fabric menu so user can select more
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "0":  # Back to Main Menu
                    send_whatsapp_message(sender, MAIN_MENU_EN)
                    set_user_state(sender, {"menu": "main", "language": "en"})
                    return jsonify({"status": "success"}), 200

            # ================================================================
            # STEP 5: EVERYTHING ELSE → USE GEMINI AI
            # ================================================================
            # This is where ALL other questions go to Gemini
            print(f"Sending to Gemini: {user_text}")
            gemini_response = get_gemini_response(user_text)
            send_whatsapp_message(sender, gemini_response)
            
            # Reset to main menu after Gemini response
            set_user_state(sender, {"menu": "main", "language": "en"})

        # ================================================================
        # IMAGE MESSAGE HANDLING
        # ================================================================
        elif msg_type == "image":
            image_response = """📸 Thank you for sharing the fabric image!

Our trade managers will:
1. Identify the fabric type and quality
2. Check availability in our inventory
3. Provide specifications and pricing

Please share additional details:
• Required quantity (min. 1 pallet)
• Preferred color/variety
• Budget range

We'll respond within 2 hours.
📞 +971 4 123 4567"""
            send_whatsapp_message(sender, image_response)
            set_user_state(sender, {"menu": "main"})

        # ================================================================
        # OTHER MESSAGE TYPES
        # ================================================================
        elif msg_type in ["audio", "document", "video"]:
            send_whatsapp_message(sender, "Thank you for your message. For fabric inquiries, please send a text description or photo. Our team will assist you. 📞 +971 4 123 4567")
            set_user_state(sender, {"menu": "main"})

        else:
            send_whatsapp_message(sender, "Thank you for contacting Al Awali Trading Co LLC. Please send a text message or photo of the fabric you're interested in. 📞 +971 4 123 4567")
            set_user_state(sender, {"menu": "main"})

    except Exception as e:
        print("WEBHOOK ERROR:", str(e))
        try:
            if sender:
                send_whatsapp_message(sender, "We encountered an error. Please try again or contact our sales team: +971 4 123 4567")
        except:
            pass

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

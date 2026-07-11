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

IMPORTANT RULES:
1. Always respond in the SAME LANGUAGE as the customer
2. Keep replies short (2-3 sentences maximum)
3. We ONLY sell wholesale fabric. MOQ is 1 pallet or container
4. Always include our contact: +971 4 123 4567
5. Be professional and helpful

COMPANY INFO:
- Name: Al Awali Trading Co LLC
- Location: Al Sabkha, Deira, Dubai, UAE
- Business: Premium fabric wholesale trading
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
# FABRIC DETAILS
# ==============================================================================

FABRIC_RESPONSES = {
    "1": "🧵 *Abaya & Black Fabrics*\n\nPremium abaya fabrics including crepe, nidha, and jersey.\nAvailable in black, navy, and dark shades.\nMOQ: 1 pallet.\n\nContact sales: +971 4 123 4567",
    "2": "👗 *Dress & Fashion Fabrics*\n\nChiffon, georgette, viscose, and printed fabrics.\nLatest designs and colors available.\nMOQ: 1 pallet.\n\nContact sales: +971 4 123 4567",
    "3": "🌿 *Cotton Fabrics*\n\n100% cotton in poplin, oxford, twill, and denim.\nIdeal for shirts, dresses, and home textiles.\nMOQ: 1 pallet.\n\nContact sales: +971 4 123 4567",
    "4": "🧵 *Linen Fabrics*\n\nPure linen and linen blends.\nBreathable, durable, and elegant.\nMOQ: 1 pallet.\n\nContact sales: +971 4 123 4567",
    "5": "✨ *Silk Fabrics*\n\nLuxury pure silk, silk blends, and satin.\nPerfect for high-end fashion.\nMOQ: 1 pallet.\n\nContact sales: +971 4 123 4567",
    "6": "🎨 *Embroidery & Designer Fabrics*\n\nExclusive embroidered and designer fabrics.\nCustom designs available.\nMOQ: 1 pallet.\n\nContact sales: +971 4 123 4567",
    "7": "👔 *Suiting Fabrics*\n\nPremium suiting for men and women.\nWool blends and stretch fabrics.\nMOQ: 1 pallet.\n\nContact sales: +971 4 123 4567",
    "8": "📦 *Other Fabrics*\n\nSpecialized technical textiles and custom orders.\nContact our team: +971 4 123 4567"
}

# ==============================================================================
# KEYWORD-BASED RESPONSES (BEFORE GEMINI)
# ==============================================================================

def get_keyword_response(user_text):
    """Check for specific keywords and return pre-defined responses"""
    
    text = user_text.lower().strip()
    
    # --- LOCATION related ---
    location_keywords = ["location", "address", "where", "office", "come", "visit", 
                         "map", "direction", "موقع", "عنوان", "पता", "адрес",
                         "කොහෙද", "ලිපිනය", "කාර්යාලය"]
    
    if any(keyword in text for keyword in location_keywords):
        return "📍 *Al Awali Trading Co LLC Head Office*\n\nAl Sabkha, Deira, Dubai\nUnited Arab Emirates\n\n🕐 Business Hours:\nSunday-Thursday: 9AM-6PM (GMT+4)\nFriday: Closed\nSaturday: 10AM-2PM\n\n📞 +971 4 123 4567\n📧 sales@alawalitrading.com\n\nA location map card has been shared above. 👆"
    
    # --- PRICE / COST related ---
    price_keywords = ["price", "cost", "rate", "quotation", "quote", "how much", 
                      "pricing", "expensive", "cheap", "budget", "මිල", "වටිනාකම"]
    
    if any(keyword in text for keyword in price_keywords):
        return "💰 *Pricing Information*\n\nOur fabric prices vary based on:\n• Fabric type and quality\n• Order quantity (MOQ: 1 pallet)\n• Shipping destination\n• Payment terms\n\nFor a custom quote, please send us:\n1. Fabric type/name\n2. Required quantity\n3. Quality preference\n\n📞 Request a quote: +971 4 123 4567\n📧 sales@alawalitrading.com"
    
    # --- AVAILABILITY related ---
    availability_keywords = ["available", "stock", "inventory", "have", "got", "exist",
                             "in stock", "out of stock", "තිබෙනවා", "ඇත්තේ"]
    
    if any(keyword in text for keyword in availability_keywords):
        return "✅ *Stock Availability*\n\nWe maintain extensive fabric inventory including:\n• Abaya Fabrics - ✓ In Stock\n• Cotton Fabrics - ✓ In Stock\n• Linen Fabrics - ✓ In Stock\n• Silk Fabrics - ⚠️ Limited\n• Designer Fabrics - 🏭 Made to Order\n\nTo check specific items, please send:\n• Fabric code or description\n• Required quantity\n\n📞 Confirm availability: +971 4 123 4567"
    
    # --- CONTACT / SALES related ---
    contact_keywords = ["contact", "sales", "call", "phone", "email", "reach", "talk",
                        "speak", "human", "agent", "customer service", "support",
                        "අමතන්න", "ෆෝන්", "ඉමේල්"]
    
    if any(keyword in text for keyword in contact_keywords):
        return "📞 *Contact Al Awali Trading Co LLC*\n\n📍 Head Office:\nAl Sabkha, Deira, Dubai, UAE\n\n📱 Phone: +971 4 123 4567\n📧 Email: sales@alawalitrading.com\n🌐 Website: www.alawalitrading.com\n\n📱 WhatsApp: +971 54 218 0677\n\n🕐 Business Hours:\nSun-Thu: 9AM-6PM (GMT+4)\nFri: Closed\nSat: 10AM-2PM\n\nWe respond within 24 hours!"
    
    # --- WHOLESALE / BULK related ---
    wholesale_keywords = ["wholesale", "bulk", "container", "pallet", "large order",
                          "b2b", "supplier", "quantity", "MOQ", "minimum order",
                          "තොග", "කන්ටේනර්"]
    
    if any(keyword in text for keyword in wholesale_keywords):
        return "📦 *Wholesale & Bulk Orders*\n\nAl Awali Trading Co LLC - B2B Fabric Supplier\n\n✅ Benefits:\n• Competitive bulk pricing\n• MOQ: 1 Pallet (500-1000 meters)\n• Container shipping available\n• Flexible payment terms\n• Custom packaging\n• Quality guaranteed\n\n🚢 Shipping worldwide\n\n📞 Wholesale team: +971 4 123 4567\n📧 bulk@alawalitrading.com"
    
    # --- SHIPPING / DELIVERY related ---
    delivery_keywords = ["delivery", "shipping", "ship", "transport", "logistics",
                         "cargo", "freight", "courier", "deliver", "shipment",
                         "ගෙන්වීම", "ප්‍රවාහනය"]
    
    if any(keyword in text for keyword in delivery_keywords):
        return "🚚 *Shipping & Delivery*\n\nGlobal shipping available:\n\n📦 Sea Freight: 2-4 weeks\n✈️ Air Freight: 3-7 days\n🚛 Land Transport: 5-7 days (GCC)\n\n📋 Documents provided:\n• Commercial Invoice\n• Packing List\n• Certificate of Origin\n• Bill of Lading/AWB\n• Quality Certificate\n\nShipping costs vary by destination and volume.\n\n📞 Get shipping quote: +971 4 123 4567"
    
    # --- SAMPLES related ---
    sample_keywords = ["sample", "photo", "picture", "image", "reference", "design",
                       "pattern", "color", "swatch", "example", "ඡායාරූපය", "නියැදිය"]
    
    if any(keyword in text for keyword in sample_keywords):
        return "📸 *Fabric Samples*\n\nHow to request samples:\n\n1️⃣ Send us a photo of your desired fabric\n2️⃣ Describe the fabric type and quality\n3️⃣ Tell us your requirements\n\n✅ Physical samples available for serious inquiries\n• Free for registered businesses\n• Shipping charges may apply\n\n📧 Send requests to: samples@alawalitrading.com\n📱 WhatsApp: +971 54 218 0677\n\nWe'll respond within 2 hours!"
    
    # --- COMPANY / ABOUT related ---
    company_keywords = ["about", "company", "alawali", "who", "profile", "history",
                        "established", "since", "mission", "vision", "හැඳින්වීම"]
    
    if any(keyword in text for keyword in company_keywords):
        return "🏢 *About Al Awali Trading Co LLC*\n\nEstablished in Dubai, UAE, we are a premier B2B textile trading company.\n\n🌍 Our Mission:\nConnecting global textile manufacturers with businesses worldwide.\n\n✅ Our Services:\n• Import premium fabric rolls globally\n• Export wholesale fabric supplies\n• Supply to GCC and worldwide\n• Custom sourcing\n\n🏭 Partner with leading manufacturers from Europe, Asia, and the Middle East.\n\n💎 Specializing in:\nAbaya Fabrics | Fashion Fabrics | Cotton | Linen | Silk | Designer Fabrics\n\n📞 Learn more: +971 4 123 4567"
    
    # --- GREETINGS (extra) ---
    greeting_keywords = ["thank", "thanks", "good morning", "good afternoon", "good evening"]
    
    if any(keyword in text for keyword in greeting_keywords):
        return "🙏 Thank you for contacting Al Awali Trading Co LLC.\n\nWe're happy to assist you with your fabric requirements.\n\nHow can we help you today?\n\n📞 +971 4 123 4567\n📧 sales@alawalitrading.com"
    
    # --- HELP / SUPPORT ---
    help_keywords = ["help", "support", "assist", "guide", "suggest", "recommend"]
    
    if any(keyword in text for keyword in help_keywords):
        return "💡 *How can we help you?*\n\nAt Al Awali Trading Co LLC, we specialize in wholesale fabric supply.\n\nWe can assist with:\n• Fabric sourcing and selection\n• Wholesale pricing and quotations\n• Bulk orders and shipping\n• Quality verification\n• Custom orders\n\n📞 Call us: +971 4 123 4567\n📧 Email: sales@alawalitrading.com\n\nOr type your specific question!"
    
    # No keyword match
    return None

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
        print(f"Sending to Gemini: {message}")
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        data = response.json()
        print("Gemini Response:", data)  # Debug log
        
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Thank you for contacting Al Awali Trading Co LLC. Our team will assist you shortly. Call +971 4 123 4567"
            
    except requests.exceptions.Timeout:
        print("Gemini API Timeout")
        return "We're experiencing high volume. Please contact our sales team directly at +971 4 123 4567"
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
        "version": "3.1.0",
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

            # --- STEP 1: GREETINGS ---
            greeting_keywords = ["hi", "hello", "hey", "salam", "assalamualaikum", 
                               "assalam", "привет", "здравствуйте", "مرحبا", 
                               "नमस्ते", "හලෝ", "ආයුබෝවන්"]
            
            if any(greeting in clean_text for greeting in greeting_keywords):
                send_whatsapp_message(sender, WELCOME_MESSAGE)
                set_user_state(sender, {"menu": "welcome"})
                return jsonify({"status": "success"}), 200

            # --- STEP 2: LANGUAGE SELECTION (A, B, C, D) ---
            if clean_num in ["a", "а"]:
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

            # --- STEP 3: MAIN MENU (1-9) ---
            if current_menu == "main":
                if clean_num == "1":
                    send_whatsapp_message(sender, FABRIC_MENU_EN)
                    set_user_state(sender, {"menu": "fabric_categories"})
                    return jsonify({"status": "success"}), 200
                elif clean_num == "2":
                    send_whatsapp_message(sender, "📋 *Quotation Request*\n\nPlease provide:\n• Fabric type\n• Quantity (min. 1 pallet)\n• Quality requirements\n• Delivery location\n\n📞 +971 4 123 4567")
                    return jsonify({"status": "success"}), 200
                elif clean_num == "3":
                    send_whatsapp_message(sender, "📦 *Wholesale Orders*\n\nMOQ: 1 Pallet\n✓ Competitive pricing\n✓ Global shipping\n✓ Custom packaging\n\n📞 +971 4 123 4567")
                    return jsonify({"status": "success"}), 200
                elif clean_num == "4":
                    send_whatsapp_message(sender, "✅ *Availability Check*\n\nSend us:\n• Fabric code/description\n• Required quantity\n\n📞 +971 4 123 4567")
                    return jsonify({"status": "success"}), 200
                elif clean_num == "5":
                    send_whatsapp_message(sender, "📸 *Send Sample Photo*\n\nShare a photo of the fabric you need.\nOur team will identify it.\n\n📞 +971 4 123 4567")
                    return jsonify({"status": "success"}), 200
                elif clean_num == "6":
                    send_whatsapp_message(sender, "🚚 *Shipping*\n\nSea: 2-4 weeks\nAir: 3-7 days\nLand (GCC): 5-7 days\n\n📞 +971 4 123 4567")
                    return jsonify({"status": "success"}), 200
                elif clean_num == "7":
                    # Send location card AND text
                    send_location(sender)
                    send_whatsapp_message(sender, "📍 *Our Location*\n\nAl Awali Trading Co LLC\nAl Sabkha, Deira, Dubai\nUnited Arab Emirates\n\n🕐 Sun-Thu: 9AM-6PM\nFri: Closed\nSat: 10AM-2PM\n\n📞 +971 4 123 4567")
                    return jsonify({"status": "success"}), 200
                elif clean_num == "8":
                    send_whatsapp_message(sender, "📞 *Sales Team*\n\n📱 WhatsApp: +971 54 218 0677\n📞 Phone: +971 4 123 4567\n📧 Email: sales@alawalitrading.com\n🌐 Website: www.alawalitrading.com")
                    return jsonify({"status": "success"}), 200
                elif clean_num == "9":
                    send_whatsapp_message(sender, WELCOME_MESSAGE)
                    set_user_state(sender, {"menu": "welcome"})
                    return jsonify({"status": "success"}), 200

            # --- STEP 4: FABRIC CATEGORIES (1-8) ---
            elif current_menu == "fabric_categories":
                if clean_num in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    response = FABRIC_RESPONSES.get(clean_num, "Contact sales: +971 4 123 4567")
                    send_whatsapp_message(sender, response)
                    return jsonify({"status": "success"}), 200
                elif clean_num == "0":
                    send_whatsapp_message(sender, MAIN_MENU_EN)
                    set_user_state(sender, {"menu": "main"})
                    return jsonify({"status": "success"}), 200

            # ================================================================
            # STEP 5: KEYWORD CHECK (BEFORE GEMINI)
            # ================================================================
            keyword_response = get_keyword_response(user_text)
            if keyword_response:
                print(f"Keyword matched! Response: {keyword_response[:100]}...")
                
                # If location, also send location card
                if any(word in user_text.lower() for word in ["location", "address", "office", "visit"]):
                    send_location(sender)
                
                send_whatsapp_message(sender, keyword_response)
                set_user_state(sender, {"menu": "main"})
                return jsonify({"status": "success"}), 200

            # ================================================================
            # STEP 6: EVERYTHING ELSE → GEMINI AI
            # ================================================================
            print(f"No keyword match. Sending to Gemini: {user_text}")
            gemini_response = get_gemini_response(user_text)
            
            # If Gemini response is generic, add contact info
            if len(gemini_response) < 50 or "team will assist" in gemini_response:
                gemini_response = gemini_response + "\n\n📞 For immediate assistance: +971 4 123 4567"
            
            send_whatsapp_message(sender, gemini_response)
            set_user_state(sender, {"menu": "main"})

        # ================================================================
        # IMAGE MESSAGE
        # ================================================================
        elif msg_type == "image":
            send_whatsapp_message(sender, "📸 *Fabric Image Received*\n\nOur trade managers will review your fabric image and provide details shortly.\n\nPlease share:\n• Required quantity\n• Preferred color/variety\n\n📞 +971 4 123 4567")
            set_user_state(sender, {"menu": "main"})

        else:
            send_whatsapp_message(sender, "Thank you for contacting Al Awali Trading Co LLC. 📞 +971 4 123 4567")
            set_user_state(sender, {"menu": "main"})

    except Exception as e:
        print("WEBHOOK ERROR:", str(e))
        try:
            if sender:
                send_whatsapp_message(sender, "We encountered an error. Please try again or call +971 4 123 4567")
        except:
            pass

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

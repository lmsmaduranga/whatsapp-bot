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
    "💬 Or just type your question!"
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
    "↩️ Reply *0* to go Back to Main Menu"
)

# ==============================================================================
# PRE-DEFINED ANSWERS FOR ALL MENU OPTIONS
# ==============================================================================

# --- ANSWER 1: Browse Fabric Collections ---
ANSWER_FABRIC_COLLECTIONS = FABRIC_MENU_EN

# --- ANSWER 2: Request a Fabric Quotation ---
ANSWER_QUOTATION = """📋 *Fabric Quotation Request*

Thank you for your interest in Al Awali Trading Co LLC.

To provide you with an accurate quotation, please share:

📌 *Required Information:*
• Fabric type and specifications
• Quantity required (MOQ: 1 pallet/container)
• Quality grade (Premium / Standard)
• Preferred color/variety
• Delivery location
• Budget range

💡 *What we offer:*
✓ Competitive wholesale pricing
✓ Bulk quantity discounts
✓ Flexible payment terms
✓ Global shipping options

📞 *Contact our quotations team:*
Phone: +971 4 123 4567
Email: quotes@alawalitrading.com
WhatsApp: +971 54 218 0677

⏰ We respond within 24 hours!

*Reply with your requirements or send a fabric image for faster service.*"""

# --- ANSWER 3: Wholesale / Bulk Order Inquiry ---
ANSWER_WHOLESALE = """📦 *Wholesale & Bulk Order Information*

Al Awali Trading Co LLC - Your Trusted B2B Fabric Supplier

✅ *Wholesale Benefits:*
• Competitive bulk pricing
• MOQ: 1 Pallet (500-1000 meters)
• Container shipping available (20ft / 40ft)
• Flexible payment terms (LC, TT, DP)
• Custom packaging options
• Quality guaranteed with certificates

📋 *Order Process:*
1. Send fabric requirements
2. Receive quotation
3. Sample approval
4. Place order
5. Production & shipping
6. Delivery & inspection

🚢 *Shipping Options:*
• Sea Freight - Economical (2-4 weeks)
• Air Freight - Express (3-7 days)
• Land Transport - GCC countries (5-7 days)

💰 *Payment Terms:*
• 30% Advance + 70% against documents
• LC at sight
• TT payment

📞 *Wholesale Team:*
Phone: +971 4 123 4567
Email: bulk@alawalitrading.com
WhatsApp: +971 54 218 0677

*Contact us for a custom wholesale quote!*"""

# --- ANSWER 4: Check Product Availability ---
ANSWER_AVAILABILITY = """✅ *Product Availability Check*

Al Awali Trading Co LLC maintains extensive fabric inventory.

📌 *To check availability, please provide:*
• Fabric code or detailed description
• Required quantity
• Preferred color/variety
• Quality grade

🔄 *Current Inventory Status:*
• Abaya & Black Fabrics - ✅ In Stock
• Cotton Fabrics (Poplin, Oxford, Twill) - ✅ In Stock
• Linen Fabrics - ✅ In Stock
• Silk Fabrics - ⚠️ Limited Stock
• Embroidered Fabrics - 🏭 Made to Order
• Suiting Fabrics - ✅ In Stock
• Designer Fabrics - 🏭 Made to Order

📋 *What happens next:*
• Our team checks inventory (within 2 hours)
• We confirm availability
• We provide specifications
• Sample available on request

📞 *Availability Team:*
Phone: +971 4 123 4567
Email: stock@alawalitrading.com
WhatsApp: +971 54 218 0677

*Send us your fabric requirements and we'll check availability immediately!*"""

# --- ANSWER 5: Send Fabric Sample / Reference Image ---
ANSWER_SAMPLE = """📸 *Fabric Sample & Reference Image*

Share your fabric requirements with us!

📌 *How to send samples:*

1️⃣ *Send a photo/image*
• Take a clear photo of the fabric
• Include close-up of texture
• Show color accurately

2️⃣ *Describe the fabric*
• Fabric type (Cotton, Silk, Linen, etc.)
• Weight (Light / Medium / Heavy)
• Pattern (Plain, Striped, Printed)
• Color preference

3️⃣ *Physical samples*
• Available for serious inquiries
• Free for registered businesses
• Shipping charges may apply

💡 *What our team does:*
• Identify fabric type and quality
• Check availability
• Provide specifications
• Suggest alternatives

📩 *Send samples to:*
Email: samples@alawalitrading.com
WhatsApp: +971 54 218 0677

📞 +971 4 123 4567

*Upload your fabric image now or share details!*"""

# --- ANSWER 6: Delivery & Shipping Information ---
ANSWER_DELIVERY = """🚚 *Delivery & Shipping Information*

Al Awali Trading Co LLC offers worldwide shipping!

📦 *Shipping Methods:*

| Method | Timeframe | Best For |
|--------|-----------|----------|
| Sea Freight | 2-4 weeks | Large orders, Economical |
| Air Freight | 3-7 days | Urgent, Small orders |
| Land Transport | 5-7 days | GCC countries |
| Express Courier | 2-5 days | Sample shipments |

🌍 *Shipping Destinations:*
• GCC Countries - 5-7 days
• Asia & Africa - 2-3 weeks
• Europe & Americas - 3-4 weeks
• Australia - 4-5 weeks

📋 *Shipping Documents Provided:*
✓ Commercial Invoice
✓ Packing List
✓ Certificate of Origin
✓ Bill of Lading / Airway Bill
✓ Quality Certificate
✓ Insurance Certificate (upon request)

💰 *Shipping Costs:*
• Based on order volume and destination
• Free shipping for orders above 5 containers
• Competitive freight rates

📞 *Logistics Team:*
Phone: +971 4 123 4567
Email: logistics@alawalitrading.com
WhatsApp: +971 54 218 0677

*Contact us for a shipping quote!*"""

# --- ANSWER 7: Our Location ---
ANSWER_LOCATION = """📍 *Al Awali Trading Co LLC Head Office*

🏢 *Address:*
Al Sabkha, Deira,
Dubai, United Arab Emirates

🕐 *Business Hours:*
Sunday - Thursday: 9:00 AM - 6:00 PM (GMT+4)
Friday: Closed
Saturday: 10:00 AM - 2:00 PM

📞 *Contact:*
Phone: +971 4 123 4567
Email: info@alawalitrading.com

📍 *Nearby Landmarks:*
• Near Al Sabkha Bus Station
• Close to Deira City Centre
• Opposite to Al Ghurair Centre

🚗 *Parking:*
Parking available nearby

🚇 *Metro:*
Nearest: Al Rigga Metro Station
(10 min walk)

*Reply with 8 to get contact information!*

📍 Location map shared above 👆"""

# --- ANSWER 8: Contact Our Sales Team ---
ANSWER_CONTACT = """📞 *Contact Al Awali Trading Co LLC*

We're here to help you!

📞 *Phone:*
+971 4 123 4567 (Main Office)
+971 54 218 0677 (WhatsApp)

📧 *Email:*
sales@alawalitrading.com (Sales)
quotes@alawalitrading.com (Quotations)
info@alawalitrading.com (General)

🌐 *Website:*
www.alawalitrading.com

📱 *Social Media:*
LinkedIn: /company/alawali-trading
Instagram: @alawalitrading

👤 *Sales Team:*
• Mr. Ahmed - Wholesale Inquiries
• Mr. Rashid - Fabric Specifications
• Ms. Fatima - Logistics & Shipping
• Mr. Khalid - Customer Service

🕐 *Business Hours:*
Sun-Thu: 9AM - 6PM (GMT+4)
Fri: Closed
Sat: 10AM - 2PM

📍 *Location:*
Al Sabkha, Deira, Dubai, UAE

*We respond within 24 hours!*

How can we assist you today?"""

# --- ANSWER 9: Back to Language Menu ---
ANSWER_BACK_LANGUAGE = WELCOME_MESSAGE

# --- ANSWER 0: Back to Main Menu ---
ANSWER_BACK_MAIN = MAIN_MENU_EN

# ==============================================================================
# FABRIC CATEGORY DETAILS (1-8 in Fabric Menu)
# ==============================================================================

FABRIC_DETAILS = {
    "1": """🧵 *Abaya & Black Fabrics*

Premium abaya fabrics for men and women.

📋 *Available Types:*
• Crepe - Lightweight, flowing
• Nidha - Medium weight, opaque
• Jersey - Stretchy, comfortable
• Satin - Shiny, luxurious
• Chiffon - Sheer, elegant

🎨 *Colors:*
• Black (All shades)
• Navy Blue
• Dark Grey
• Maroon
• Dark Green

📏 *Specifications:*
• Width: 58/60 inches
• Weight: 100-200 GSM
• MOQ: 1 Pallet

✨ *Features:*
• High quality
• Colorfast
• Soft texture
• Easy to drape

📞 +971 4 123 4567
📧 sales@alawalitrading.com

*Contact us for catalog and pricing!*""",

    "2": """👗 *Dress & Fashion Fabrics*

Latest fashion fabrics for modern designs!

📋 *Available Types:*
• Chiffon - Sheer, elegant
• Georgette - Textured, flowing
• Viscose - Soft, comfortable
• Polyester - Durable, versatile
• Blended fabrics

🎨 *Colors & Prints:*
• Solid colors (All shades)
• Floral prints
• Geometric patterns
• Digital prints
• Custom designs available

📏 *Specifications:*
• Width: 44-58 inches
• Weight: 80-180 GSM
• MOQ: 1 Pallet

💡 *Best For:*
• Abayas & Dresses
• Party wear
• Everyday wear
• Bridal collections

📞 +971 4 123 4567
📧 sales@alawalitrading.com

*Send us your design requirements!*""",

    "3": """🌿 *Cotton Fabrics*

Premium 100% cotton fabrics - Comfort meets quality!

📋 *Available Types:*
• Poplin - Crisp, smooth
• Oxford - Textured, durable
• Twill - Diagonal weave, strong
• Denim - Durable, casual
• Voile - Lightweight, soft
• Lawn - Fine, smooth

📏 *Specifications:*
• Width: 44-60 inches
• Weight: 100-350 GSM
• MOQ: 1 Pallet

🎨 *Colors:*
• White and off-white
• Pastel shades
• Dark colors
• Prints available

💡 *Best For:*
• Shirts & Blouses
• Dresses
• Home textiles
• Uniforms
• Kids wear

📞 +971 4 123 4567
📧 sales@alawalitrading.com

*Request your cotton fabric quote now!*""",

    "4": """🧵 *Linen Fabrics*

Natural, breathable, and elegant - Pure linen!

📋 *Available Types:*
• Pure Linen - 100% natural
• Linen Blends - Linen/Cotton, Linen/Viscose
• Washed Linen - Soft, casual
• Linen Canvas - Heavy, durable

📏 *Specifications:*
• Width: 44-58 inches
• Weight: 120-300 GSM
• MOQ: 1 Pallet

🎨 *Colors:*
• Natural/Beige
• White
• Pastel shades
• Earth tones
• Dark colors

✨ *Features:*
• Breathable
• Anti-bacterial
• Eco-friendly
• Gets softer with wear

💡 *Best For:*
• Summer wear
• Suits & Blazers
• Home textiles
• Luxury apparel

📞 +971 4 123 4567
📧 sales@alawalitrading.com

*Contact us for linen fabric pricing!*""",

    "5": """✨ *Silk Fabrics*

Luxury silk fabrics for premium fashion!

📋 *Available Types:*
• Pure Silk - 100% natural
• Silk Satin - Smooth, shiny
• Silk Chiffon - Sheer, flowing
• Silk Crepe - Textured
• Silk Georgette - Soft, elegant
• Silk Blends - Silk/Cotton, Silk/Wool

📏 *Specifications:*
• Width: 36-55 inches
• Weight: 30-120 GSM
• MOQ: 1 Pallet

🎨 *Colors:*
• All colors available
• Custom dyeing possible
• Prints available

✨ *Features:*
• Natural protein fiber
• Hypoallergenic
• Temperature regulating
• Luxurious sheen

💡 *Best For:*
• Bridal wear
• Evening gowns
• Luxury fashion
• Scarves & accessories

📞 +971 4 123 4567
📧 sales@alawalitrading.com

*Contact us for premium silk collection!*""",

    "6": """🎨 *Embroidery & Designer Fabrics*

Exclusive embroidered and designer fabrics!

📋 *Available Types:*
• Hand Embroidery - Traditional, detailed
• Machine Embroidery - Consistent, precise
• Digital Prints - Modern, vibrant
• Sequins & Beads - Glamorous
• Lace Fabrics - Delicate, elegant
• Applique - Creative designs

📏 *Specifications:*
• Width: 44-58 inches
• Custom designs available
• MOQ: 1 Pallet

🎨 *Designs:*
• Traditional patterns
• Modern designs
• Custom designs
• Arabic calligraphy
• Floral motifs

💡 *Best For:*
• Abayas (Special occasions)
• Bridal wear
• Evening wear
• Party wear
• Designer collections

📞 +971 4 123 4567
📧 sales@alawalitrading.com

*Share your design ideas with us!*""",

    "7": """👔 *Suiting Fabrics*

Premium suiting fabrics for formal wear!

📋 *Available Types:*
• Wool Blends - Warm, elegant
• Polyester Blends - Durable, affordable
• Stretch Fabrics - Comfortable
• Linen Suiting - Lightweight
• Cotton Suiting - Breathable
• Silk Blends - Luxurious

📏 *Specifications:*
• Width: 58/60 inches
• Weight: 150-350 GSM
• MOQ: 1 Pallet

🎨 *Colors:*
• Navy Blue
• Charcoal Grey
• Black
• Light Grey
• Beige
• Brown

💡 *Best For:*
• Men's suits
• Women's suits
• Blazers
• Formal wear
• Corporate wear

📞 +971 4 123 4567
📧 sales@alawalitrading.com

*Get your suiting fabric quote today!*""",

    "8": """📦 *Other Fabrics*

Specialized fabrics for all your needs!

📋 *We also supply:*
• Technical Textiles - Industrial use
• Outdoor Fabrics - Waterproof, durable
• Upholstery Fabrics - Home & office
• Curtain Fabrics - Decorative
• Uniform Fabrics - Corporate wear
• Custom Orders - Your specifications

📏 *Specifications:*
• Custom widths available
• Various weights
• MOQ: 1 Pallet

✨ *Special Services:*
• Custom sourcing
• Special treatments (Waterproof, Fire retardant)
• Custom dyeing
• Custom printing
• Private label

💡 *Industry Solutions:*
• Hospitality
• Healthcare
• Corporate
• Retail
• Industrial

📞 +971 4 123 4567
📧 sales@alawalitrading.com

*Tell us your specific requirements!*"""
}

# ==============================================================================
# CORE FUNCTIONS
# ==============================================================================

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
            print(f"✅ Message sent to {to}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
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
        print(f"❌ Location error: {str(e)}")
        return False

def get_gemini_response(message):
    """Fallback for questions not in menu"""
    if not GEMINI_API_KEY:
        return "Thank you for your question. Please contact our sales team at +971 4 123 4567 for detailed assistance."
    
    system_instruction = """
You are the expert B2B Export Trade Manager for Al Awali Trading Co LLC.

RULES:
1. Respond in the SAME language as the customer
2. Keep replies short and professional (3-5 sentences)
3. We sell wholesale fabrics only. MOQ: 1 pallet/container
4. Always include: +971 4 123 4567

COMPANY: Al Awali Trading Co LLC, Al Sabkha, Deira, Dubai, UAE
"""
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"role": "user", "parts": [{"text": message}]}],
        "systemInstruction": {"parts": [{"text": system_instruction}]}
    }
    
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=30)
        data = response.json()
        
        if "candidates" in data and len(data["candidates"]) > 0:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Thank you for contacting Al Awali Trading Co LLC. How can we assist you? 📞 +971 4 123 4567"
    except Exception as e:
        print(f"❌ Gemini Error: {str(e)}")
        return "Thank you for your question. Our team will assist you. Contact: +971 4 123 4567"

# ==============================================================================
# USER STATE MANAGEMENT
# ==============================================================================

user_states = {}

def get_user_state(user_id):
    return user_states.get(user_id, {"menu": "welcome"})

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
        "version": "5.0.0"
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
        print("📨 Webhook received")
        
        value = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
        if "messages" not in value:
            return jsonify({"status": "ignored"}), 200

        message = value["messages"][0]
        sender = message["from"]
        msg_type = message["type"]

        user_state = get_user_state(sender)
        current_menu = user_state.get("menu", "welcome")

        if msg_type == "text":
            user_text = message["text"]["body"].strip()
            clean_text = user_text.lower()
            clean_num = clean_text.replace(".", "")

            print(f"👤 User: {sender}")
            print(f"💬 Text: {user_text}")
            print(f"📋 Menu: {current_menu}")

            # --- STEP 1: GREETINGS ---
            greeting_keywords = ["hi", "hello", "hey", "salam", "assalamualaikum",
                               "привет", "مرحبا", "नमस्ते", "හලෝ", "ආයුබෝවන්"]
            
            if any(greeting in clean_text for greeting in greeting_keywords):
                send_whatsapp_message(sender, WELCOME_MESSAGE)
                set_user_state(sender, {"menu": "welcome"})
                return jsonify({"status": "success"}), 200

            # --- STEP 2: LANGUAGE SELECTION ---
            if clean_num in ["a", "а"]:
                send_whatsapp_message(sender, MAIN_MENU_EN)
                set_user_state(sender, {"menu": "main"})
                return jsonify({"status": "success"}), 200
            elif clean_num == "b":
                send_whatsapp_message(sender, MAIN_MENU_AR)
                set_user_state(sender, {"menu": "main"})
                return jsonify({"status": "success"}), 200
            elif clean_num == "c":
                send_whatsapp_message(sender, MAIN_MENU_HI)
                set_user_state(sender, {"menu": "main"})
                return jsonify({"status": "success"}), 200
            elif clean_num == "d":
                send_whatsapp_message(sender, MAIN_MENU_RU)
                set_user_state(sender, {"menu": "main"})
                return jsonify({"status": "success"}), 200

            # --- STEP 3: MAIN MENU (1-9) ---
            if current_menu == "main":
                if clean_num == "1":
                    send_whatsapp_message(sender, ANSWER_FABRIC_COLLECTIONS)
                    set_user_state(sender, {"menu": "fabric_categories"})
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "2":
                    send_whatsapp_message(sender, ANSWER_QUOTATION)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "3":
                    send_whatsapp_message(sender, ANSWER_WHOLESALE)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "4":
                    send_whatsapp_message(sender, ANSWER_AVAILABILITY)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "5":
                    send_whatsapp_message(sender, ANSWER_SAMPLE)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "6":
                    send_whatsapp_message(sender, ANSWER_DELIVERY)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "7":
                    send_location(sender)
                    send_whatsapp_message(sender, ANSWER_LOCATION)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "8":
                    send_whatsapp_message(sender, ANSWER_CONTACT)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "9":
                    send_whatsapp_message(sender, ANSWER_BACK_LANGUAGE)
                    set_user_state(sender, {"menu": "welcome"})
                    return jsonify({"status": "success"}), 200

            # --- STEP 4: FABRIC CATEGORIES (1-8) ---
            elif current_menu == "fabric_categories":
                if clean_num in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    response = FABRIC_DETAILS.get(clean_num, "Fabric details available. Contact: +971 4 123 4567")
                    send_whatsapp_message(sender, response)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "0":
                    send_whatsapp_message(sender, ANSWER_BACK_MAIN)
                    set_user_state(sender, {"menu": "main"})
                    return jsonify({"status": "success"}), 200

            # --- STEP 5: EVERYTHING ELSE → GEMINI (Fallback) ---
            print("🤖 Sending to Gemini (fallback)...")
            gemini_response = get_gemini_response(user_text)
            send_whatsapp_message(sender, gemini_response)
            set_user_state(sender, {"menu": "main"})

        # --- IMAGE MESSAGE ---
        elif msg_type == "image":
            send_whatsapp_message(sender, "📸 Thank you for sharing the fabric image! Our trade managers will review it and provide specifications and pricing within 2 hours. 📞 +971 4 123 4567")
            set_user_state(sender, {"menu": "main"})

        else:
            send_whatsapp_message(sender, "Thank you for contacting Al Awali Trading Co LLC. 📞 +971 4 123 4567")
            set_user_state(sender, {"menu": "main"})

    except Exception as e:
        print(f"❌ WEBHOOK ERROR: {str(e)}")
        try:
            if sender:
                send_whatsapp_message(sender, "We encountered an error. Please try again or call +971 4 123 4567")
        except:
            pass

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

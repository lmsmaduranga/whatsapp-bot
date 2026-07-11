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
5. Always maintain a helpful and professional tone.
6. For fabric inquiries, ask for specific details like quantity, type, and quality requirements.
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
    "9️⃣ Back to Language Menu\n\n"
    "💬 Or type your question directly!"
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
    "9️⃣ العودة إلى قائمة اللغة\n\n"
    "💬 أو اكتب سؤالك مباشرة!"
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
    "9️⃣ भाषा मेनू पर वापस जाएं\n\n"
    "💬 या सीधे अपना प्रश्न टाइप करें!"
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
    "9️⃣ Вернуться к выбору языка\n\n"
    "💬 Или задайте свой вопрос напрямую!"
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
    "💬 Or describe what you're looking for!"
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
    return jsonify({
        "status": "running", 
        "service": "Al Awali WhatsApp Bot",
        "version": "1.0.0"
    }), 200

def get_gemini_response(message):
    """Get response from Gemini API with proper error handling"""
    if not GEMINI_API_KEY:
        return "Sorry, AI service is temporarily unavailable. Please contact our sales team directly."
    
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
            print("Gemini API Response:", data)
            return "Thank you for contacting Al Awali Trading Co LLC. Our team will assist you shortly."
            
    except requests.exceptions.Timeout:
        print("Gemini API Timeout")
        return "We're experiencing high volume. Please contact our sales team directly for immediate assistance."
    except Exception as e:
        print("Gemini Error:", str(e))
        return "Thank you for contacting Al Awali Trading Co LLC. Our team will assist you shortly."

def send_whatsapp_message(to, text):
    """Send WhatsApp message with proper error handling"""
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("WhatsApp credentials missing")
        return False
    
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
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Message sent successfully to {to}")
            return True
        else:
            print(f"Failed to send message: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return False

def send_location(to):
    """Send location card"""
    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        return False
    
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
    
    try:
        response = requests.post(url, json=payload, headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}", 
            "Content-Type": "application/json"
        }, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"Error sending location: {str(e)}")
        return False

def process_fabric_inquiry(user_message, sender):
    """Process fabric-related inquiries with Gemini"""
    prompt = f"""
    Customer asked about fabrics: "{user_message}"
    
    Respond professionally as Al Awali Trading Co LLC Trade Manager.
    - Ask about specific fabric type, quantity, and quality requirements
    - Mention MOQ (1 pallet/container)
    - Offer to connect with sales team for detailed quotations
    - Keep response short (2-3 sentences)
    """
    return get_gemini_response(prompt)

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
    try:
        data = request.get_json()
        print("Webhook received:", data)  # Debug log
        
        value = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
        if "messages" not in value:
            return jsonify({"status": "ignored"}), 200

        message = value["messages"][0]
        sender = message["from"]
        msg_type = message["type"]

        # Handle text messages
        if msg_type == "text":
            user_text = message["text"]["body"].strip()
            clean_text = user_text.lower()
            clean_num = clean_text.replace(".", "")

            # --- GREETING DETECTION ---
            greeting_keywords = ["hi", "hello", "hey", "salam", "assalamualaikum", "assalam", 
                               "привет", "здравствуйте", "مرحبا", "السلام عليكم", "नमस्ते"]
            
            if any(greeting in clean_text for greeting in greeting_keywords):
                send_whatsapp_message(sender, WELCOME_MESSAGE)
                return jsonify({"status": "success"}), 200

            # --- LANGUAGE SELECTION (A, B, C, D) ---
            if clean_num in ["a", "а"]:  # English
                send_whatsapp_message(sender, MAIN_MENU_EN)
                return jsonify({"status": "success"}), 200
            elif clean_num == "b":  # Arabic
                send_whatsapp_message(sender, MAIN_MENU_AR)
                return jsonify({"status": "success"}), 200
            elif clean_num == "c":  # Hindi
                send_whatsapp_message(sender, MAIN_MENU_HI)
                return jsonify({"status": "success"}), 200
            elif clean_num == "d":  # Russian
                send_whatsapp_message(sender, MAIN_MENU_RU)
                return jsonify({"status": "success"}), 200

            # --- MAIN MENU OPTIONS (1-9) ---
            if clean_num == "1":  # Browse Fabric Collections
                send_whatsapp_message(sender, FABRIC_MENU_EN)
                return jsonify({"status": "success"}), 200
            
            elif clean_num == "7":  # Location
                if send_location(sender):
                    reply = "📍 Location shared above. Our office is in Al Sabkha, Deira, Dubai. Visit us during business hours!"
                    send_whatsapp_message(sender, reply)
                else:
                    send_whatsapp_message(sender, "Sorry, we couldn't send the location. Please visit: Al Sabkha, Deira, Dubai.")
                return jsonify({"status": "success"}), 200
                
            elif clean_num == "9":  # Back to Language Menu
                send_whatsapp_message(sender, WELCOME_MESSAGE)
                return jsonify({"status": "success"}), 200
                
            elif clean_num == "0":  # Back to Main Menu
                send_whatsapp_message(sender, MAIN_MENU_EN)
                return jsonify({"status": "success"}), 200

            elif clean_num == "8":  # Contact Sales Team
                reply = "📞 Our sales team is ready to assist you!\n\nContact: +971 4 123 4567\nEmail: sales@alawalitrading.com\n\nWe'll respond within 24 hours."
                send_whatsapp_message(sender, reply)
                return jsonify({"status": "success"}), 200

            # --- FABRIC CATEGORIES (2-8 in submenu) ---
            if clean_num in ["2", "3", "4", "5", "6"]:
                # Provide sample details for fabric categories
                send_whatsapp_message(sender, SAMPLE_DETAILS_EN)
                # Send a follow-up message asking for more details
                follow_up = "For pricing and availability, please provide: Fabric type, Quantity, Quality requirements."
                send_whatsapp_message(sender, follow_up)
                return jsonify({"status": "success"}), 200

            # --- FABRIC RELATED KEYWORDS ---
            fabric_keywords = ["fabric", "cloth", "textile", "material", "cotton", "silk", "linen", 
                             "abaya", "dress", "suit", "embroidery", "قطن", "حرير", "कपड़ा", "ткань"]
            
            if any(keyword in clean_text for keyword in fabric_keywords):
                response = process_fabric_inquiry(user_text, sender)
                send_whatsapp_message(sender, response)
                return jsonify({"status": "success"}), 200

            # --- GENERAL INQUIRIES ---
            # If no specific command matched, use Gemini
            gemini_response = get_gemini_response(user_text)
            
            # If Gemini response is too generic, add a professional touch
            if len(gemini_response) < 50:
                gemini_response = f"{gemini_response}\n\nFor immediate assistance, please contact our sales team at +971 4 123 4567."
            
            send_whatsapp_message(sender, gemini_response)

        # Handle image messages
        elif msg_type == "image":
            reply = "📸 Thank you for sharing the fabric image. Our trade managers will review the fabric quality and availability. We'll get back to you shortly with details."
            send_whatsapp_message(sender, reply)
            
            # Send a follow-up question
            follow_up = "To help us better assist you, please let us know:\n- Quantity needed\n- Preferred color\n- Budget range"
            send_whatsapp_message(sender, follow_up)

        # Handle other message types
        elif msg_type in ["audio", "document", "video"]:
            send_whatsapp_message(sender, "Thank you for your message. For fabric inquiries, please send us a text description or image, and our team will assist you.")

        else:
            send_whatsapp_message(sender, "Thank you for contacting Al Awali Trading Co LLC. Please send us a text message or image of the fabric you're interested in.")

    except Exception as e:
        print("WEBHOOK ERROR:", str(e))
        # Try to send an error message to the user
        try:
            if sender:
                send_whatsapp_message(sender, "We encountered an error processing your request. Please try again or contact our sales team directly.")
        except:
            pass

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

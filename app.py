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
# MULTILINGUAL MENUS - ALL LANGUAGES
# ==============================================================================

# --- WELCOME MESSAGE (All Languages) ---
WELCOME_EN = (
    "👋 Welcome to Al Awali Trading Co. LLC.\n\n"
    "Thank you for contacting us.\n\n"
    "We are a trusted textile trading company based in the UAE, specializing in sourcing and supplying high-quality fabrics and textile products from leading manufacturers around the world.\n\n"
    "To continue, please select your preferred language:\n"
    "🇬🇧 A. English\n"
    "🇦🇪 B. العربية (Arabic)\n"
    "🇮🇳 C. हिन्दी / اردو (Hindi / Urdu)\n"
    "🇷🇺 D. Русский (Russian)"
)

WELCOME_AR = (
    "👋 مرحباً بكم في شركة العوالي للتجارة ذ.م.م.\n\n"
    "شكراً لتواصلكم معنا.\n\n"
    "نحن شركة تجارية موثوقة مقرها في دولة الإمارات العربية المتحدة، متخصصة في توريد وتزويد الأقمشة عالية الجودة والمنتجات النسيجية من كبرى الشركات المصنعة حول العالم.\n\n"
    "للمتابعة، يرجى اختيار لغتك المفضلة:\n"
    "🇬🇧 A. English\n"
    "🇦🇪 B. العربية (Arabic)\n"
    "🇮🇳 C. हिन्दी / اردو (Hindi / Urdu)\n"
    "🇷🇺 D. Русский (Russian)"
)

WELCOME_HI = (
    "👋 अल अवाली ट्रेडिंग कंपनी एलएलसी में आपका स्वागत है।\n\n"
    "हमसे संपर्क करने के लिए धन्यवाद।\n\n"
    "हम यूएई में स्थित एक विश्वसनीय कपड़ा व्यापार कंपनी हैं, जो दुनिया भर के अग्रणी निर्माताओं से उच्च गुणवत्ता वाले कपड़े और वस्त्र उत्पादों की सोर्सिंग और आपूर्ति में विशेषज्ञता रखती है।\n\n"
    "जारी रखने के लिए, कृपया अपनी पसंदीदा भाषा चुनें:\n"
    "🇬🇧 A. English\n"
    "🇦🇪 B. العربية (Arabic)\n"
    "🇮🇳 C. हिन्दी / اردو (Hindi / Urdu)\n"
    "🇷🇺 D. Русский (Russian)"
)

WELCOME_RU = (
    "👋 Добро пожаловать в Al Awali Trading Co LLC.\n\n"
    "Благодарим вас за обращение к нам.\n\n"
    "Мы - надежная текстильная торговая компания, базирующаяся в ОАЭ, специализирующаяся на поиске и поставке высококачественных тканей и текстильной продукции от ведущих производителей по всему миру.\n\n"
    "Чтобы продолжить, выберите предпочитаемый язык:\n"
    "🇬🇧 A. English\n"
    "🇦🇪 B. العربية (Arabic)\n"
    "🇮🇳 C. हिन्दी / اردو (Hindi / Urdu)\n"
    "🇷🇺 D. Русский (Russian)"
)

# --- MAIN MENU (All Languages) ---
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
    "5️⃣ إرسال عينة قماش / صورة مرجعية\n"
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
    "2️⃣ Запросить коммерческое предложение\n"
    "3️⃣ Оптовый заказ\n"
    "4️⃣ Проверить наличие товара\n"
    "5️⃣ Отправить образец ткани / изображение\n"
    "6️⃣ Информация о доставке\n"
    "7️⃣ Наше местоположение 📍\n"
    "8️⃣ Связаться с отделом продаж\n\n"
    "9️⃣ Вернуться к выбору языка\n\n"
    "💬 Или задайте свой вопрос напрямую!"
)

# --- FABRIC MENU (All Languages) ---
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

FABRIC_MENU_AR = (
    "🧵 *مجموعات الأقمشة لدينا*\n"
    "يرجى اختيار نوع القماش الذي تبحث عنه:\n\n"
    "1️⃣ أقمشة العباية والسوداء\n"
    "2️⃣ أقمشة الفساتين والموضة\n"
    "3️⃣ الأقمشة القطنية\n"
    "4️⃣ أقمشة الكتان\n"
    "5️⃣ أقمشة الحرير\n"
    "6️⃣ أقمشة التطريز والمصممين\n"
    "7️⃣ أقمشة البدلات\n"
    "8️⃣ أقمشة أخرى\n\n"
    "↩️ الرد *0* للعودة إلى القائمة الرئيسية"
)

FABRIC_MENU_HI = (
    "🧵 *हमारे फैब्रिक कलेक्शन*\n"
    "कृपया उस प्रकार का कपड़ा चुनें जिसे आप ढूंढ रहे हैं:\n\n"
    "1️⃣ अबाया और ब्लैक फैब्रिक\n"
    "2️⃣ ड्रेस और फैशन फैब्रिक\n"
    "3️⃣ कॉटन फैब्रिक\n"
    "4️⃣ लिनन फैब्रिक\n"
    "5️⃣ सिल्क फैब्रिक\n"
    "6️⃣ एम्ब्रॉयडरी और डिज़ाइनर फैब्रिक\n"
    "7️⃣ सूटिंग फैब्रिक\n"
    "8️⃣ अन्य फैब्रिक\n\n"
    "↩️ मुख्य मेनू पर वापस जाने के लिए *0* दबाएं"
)

FABRIC_MENU_RU = (
    "🧵 *Наши коллекции тканей*\n"
    "Пожалуйста, выберите тип ткани, который вы ищете:\n\n"
    "1️⃣ Ткани для абайи и черные ткани\n"
    "2️⃣ Платьевые и модные ткани\n"
    "3️⃣ Хлопчатобумажные ткани\n"
    "4️⃣ Льняные ткани\n"
    "5️⃣ Шелковые ткани\n"
    "6️⃣ Вышитые и дизайнерские ткани\n"
    "7️⃣ Костюмные ткани\n"
    "8️⃣ Другие ткани\n\n"
    "↩️ Ответьте *0*, чтобы вернуться в главное меню"
)

# ==============================================================================
# PRE-DEFINED ANSWERS FOR ALL OPTIONS (All Languages)
# ==============================================================================

# --- ANSWER 2: Quotation ---
ANSWER_QUOTATION_EN = """📋 *Fabric Quotation Request*

To provide an accurate quotation, please share:

• Fabric type and specifications
• Quantity required (MOQ: 1 pallet)
• Quality grade
• Delivery location

📞 +971 4 123 4567
📧 sales@alawalitrading.com"""

ANSWER_QUOTATION_AR = """📋 *طلب عرض سعر للأقمشة*

لتقديم عرض سعر دقيق، يرجى مشاركة:

• نوع القماش والمواصفات
• الكمية المطلوبة (الحد الأدنى للطلب: 1 باليت)
• درجة الجودة
• موقع التسليم

📞 +971 4 123 4567
📧 sales@alawalitrading.com"""

ANSWER_QUOTATION_HI = """📋 *फैब्रिक कोटेशन अनुरोध*

सटीक कोटेशन प्रदान करने के लिए, कृपया साझा करें:

• फैब्रिक का प्रकार और विनिर्देश
• आवश्यक मात्रा (MOQ: 1 पैलेट)
• गुणवत्ता ग्रेड
• डिलीवरी स्थान

📞 +971 4 123 4567
📧 sales@alawalitrading.com"""

ANSWER_QUOTATION_RU = """📋 *Запрос коммерческого предложения*

Для предоставления точного предложения, пожалуйста, укажите:

• Тип ткани и спецификации
• Требуемое количество (MOQ: 1 паллета)
• Сорт качества
• Место доставки

📞 +971 4 123 4567
📧 sales@alawalitrading.com"""

# --- ANSWER 3: Wholesale ---
ANSWER_WHOLESALE_EN = """📦 *Wholesale & Bulk Orders*

MOQ: 1 Pallet (500-1000 meters)

✓ Competitive pricing
✓ Global shipping
✓ Flexible payment terms
✓ Custom packaging

📞 +971 4 123 4567
📧 bulk@alawalitrading.com"""

ANSWER_WHOLESALE_AR = """📦 *الطلبات بالجملة والكميات الكبيرة*

الحد الأدنى للطلب: 1 باليت (500-1000 متر)

✓ أسعار تنافسية
✓ شحن عالمي
✓ شروط دفع مرنة
✓ تغليف مخصص

📞 +971 4 123 4567
📧 bulk@alawalitrading.com"""

ANSWER_WHOLESALE_HI = """📦 *थोक और बल्क ऑर्डर*

MOQ: 1 पैलेट (500-1000 मीटर)

✓ प्रतिस्पर्धी मूल्य निर्धारण
✓ वैश्विक शिपिंग
✓ लचीली भुगतान शर्तें
✓ कस्टम पैकेजिंग

📞 +971 4 123 4567
📧 bulk@alawalitrading.com"""

ANSWER_WHOLESALE_RU = """📦 *Оптовые заказы*

MOQ: 1 паллета (500-1000 метров)

✓ Конкурентные цены
✓ Международная доставка
✓ Гибкие условия оплаты
✓ Индивидуальная упаковка

📞 +971 4 123 4567
📧 bulk@alawalitrading.com"""

# --- ANSWER 4: Availability ---
ANSWER_AVAILABILITY_EN = """✅ *Product Availability*

Current stock:
• Abaya Fabrics - ✅ In Stock
• Cotton Fabrics - ✅ In Stock
• Linen Fabrics - ✅ In Stock
• Silk Fabrics - ⚠️ Limited

Send fabric code for specific check.

📞 +971 4 123 4567"""

ANSWER_AVAILABILITY_AR = """✅ *توفر المنتج*

المخزون الحالي:
• أقمشة العباية - ✅ متوفرة
• الأقمشة القطنية - ✅ متوفرة
• أقمشة الكتان - ✅ متوفرة
• أقمشة الحرير - ⚠️ محدودة

أرسل رمز القماش للتحقق المحدد.

📞 +971 4 123 4567"""

ANSWER_AVAILABILITY_HI = """✅ *उत्पाद उपलब्धता*

वर्तमान स्टॉक:
• अबाया फैब्रिक - ✅ स्टॉक में
• कॉटन फैब्रिक - ✅ स्टॉक में
• लिनन फैब्रिक - ✅ स्टॉक में
• सिल्क फैब्रिक - ⚠️ सीमित

विशिष्ट जांच के लिए फैब्रिक कोड भेजें।

📞 +971 4 123 4567"""

ANSWER_AVAILABILITY_RU = """✅ *Наличие товара*

Текущий склад:
• Ткани для абайи - ✅ В наличии
• Хлопчатобумажные ткани - ✅ В наличии
• Льняные ткани - ✅ В наличии
• Шелковые ткани - ⚠️ Ограничено

Отправьте код ткани для конкретной проверки.

📞 +971 4 123 4567"""

# --- ANSWER 5: Samples ---
ANSWER_SAMPLE_EN = """📸 *Fabric Samples*

Send us a photo of the fabric you need.
Our team will identify it and provide details.

📞 +971 4 123 4567
📧 samples@alawalitrading.com"""

ANSWER_SAMPLE_AR = """📸 *عينات الأقمشة*

أرسل لنا صورة للقماش الذي تحتاجه.
سيقوم فريقنا بتحديده وتقديم التفاصيل.

📞 +971 4 123 4567
📧 samples@alawalitrading.com"""

ANSWER_SAMPLE_HI = """📸 *फैब्रिक सैंपल*

हमें उस कपड़े की फोटो भेजें जो आपको चाहिए।
हमारी टीम इसे पहचानेगी और विवरण प्रदान करेगी।

📞 +971 4 123 4567
📧 samples@alawalitrading.com"""

ANSWER_SAMPLE_RU = """📸 *Образцы тканей*

Отправьте нам фото ткани, которая вам нужна.
Наша команда определит ее и предоставит информацию.

📞 +971 4 123 4567
📧 samples@alawalitrading.com"""

# --- ANSWER 6: Delivery ---
ANSWER_DELIVERY_EN = """🚚 *Delivery & Shipping*

Sea: 2-4 weeks
Air: 3-7 days
Land (GCC): 5-7 days

Shipping documents provided.

📞 +971 4 123 4567
📧 logistics@alawalitrading.com"""

ANSWER_DELIVERY_AR = """🚚 *التوصيل والشحن*

بحري: 2-4 أسابيع
جوي: 3-7 أيام
بري (دول الخليج): 5-7 أيام

يتم توفير وثائق الشحن.

📞 +971 4 123 4567
📧 logistics@alawalitrading.com"""

ANSWER_DELIVERY_HI = """🚚 *डिलीवरी और शिपिंग*

समुद्र: 2-4 सप्ताह
हवाई: 3-7 दिन
स्थल (GCC): 5-7 दिन

शिपिंग दस्तावेज़ प्रदान किए गए।

📞 +971 4 123 4567
📧 logistics@alawalitrading.com"""

ANSWER_DELIVERY_RU = """🚚 *Доставка и отправка*

Море: 2-4 недели
Воздух: 3-7 дней
Суша (GCC): 5-7 дней

Предоставляются транспортные документы.

📞 +971 4 123 4567
📧 logistics@alawalitrading.com"""

# --- ANSWER 7: Location ---
ANSWER_LOCATION_EN = """📍 *Our Location*

Al Awali Trading Co LLC
Al Sabkha, Deira, Dubai
United Arab Emirates

Sun-Thu: 9AM-6PM
Fri: Closed
Sat: 10AM-2PM

📞 +971 4 123 4567"""

ANSWER_LOCATION_AR = """📍 *موقعنا*

شركة العوالي للتجارة ذ.م.م
السبخة، ديرة، دبي
الإمارات العربية المتحدة

الأحد-الخميس: 9ص-6م
الجمعة: مغلق
السبت: 10ص-2م

📞 +971 4 123 4567"""

ANSWER_LOCATION_HI = """📍 *हमारा स्थान*

अल अवाली ट्रेडिंग कंपनी एलएलसी
अल सबखा, दीरा, दुबई
संयुक्त अरब अमीरात

रवि-गुरु: 9AM-6PM
शुक्र: बंद
शनि: 10AM-2PM

📞 +971 4 123 4567"""

ANSWER_LOCATION_RU = """📍 *Наше местоположение*

Al Awali Trading Co LLC
Аль-Сабха, Дейра, Дубай
Объединенные Арабские Эмираты

Вс-Чт: 9:00-18:00
Пт: Закрыто
Сб: 10:00-14:00

📞 +971 4 123 4567"""

# --- ANSWER 8: Contact ---
ANSWER_CONTACT_EN = """📞 *Contact Us*

Phone: +971 4 123 4567
WhatsApp: +971 54 218 0677
Email: sales@alawalitrading.com

📍 Al Sabkha, Deira, Dubai, UAE"""

ANSWER_CONTACT_AR = """📞 *اتصل بنا*

هاتف: +971 4 123 4567
واتساب: +971 54 218 0677
بريد إلكتروني: sales@alawalitrading.com

📍 السبخة، ديرة، دبي، الإمارات العربية المتحدة"""

ANSWER_CONTACT_HI = """📞 *हमसे संपर्क करें*

फोन: +971 4 123 4567
व्हाट्सएप: +971 54 218 0677
ईमेल: sales@alawalitrading.com

📍 अल सबखा, दीरा, दुबई, यूएई"""

ANSWER_CONTACT_RU = """📞 *Свяжитесь с нами*

Телефон: +971 4 123 4567
WhatsApp: +971 54 218 0677
Email: sales@alawalitrading.com

📍 Аль-Сабха, Дейра, Дубай, ОАЭ"""

# ==============================================================================
# FABRIC DETAILS (All Languages - Key info only, keep short)
# ==============================================================================

FABRIC_DETAILS_EN = {
    "1": "🧵 *Abaya & Black Fabrics*\n\nPremium abaya fabrics: Crepe, Nidha, Jersey.\nColors: Black, Navy, Dark shades.\nMOQ: 1 pallet.\n\n📞 +971 4 123 4567",
    "2": "👗 *Dress & Fashion Fabrics*\n\nChiffon, Georgette, Viscose, Printed.\nLatest designs and colors.\nMOQ: 1 pallet.\n\n📞 +971 4 123 4567",
    "3": "🌿 *Cotton Fabrics*\n\n100% Cotton: Poplin, Oxford, Twill, Denim.\nMOQ: 1 pallet.\n\n📞 +971 4 123 4567",
    "4": "🧵 *Linen Fabrics*\n\nPure Linen and Linen blends.\nBreathable, durable, elegant.\nMOQ: 1 pallet.\n\n📞 +971 4 123 4567",
    "5": "✨ *Silk Fabrics*\n\nPure Silk, Silk Satin, Silk blends.\nLuxury quality for fashion.\nMOQ: 1 pallet.\n\n📞 +971 4 123 4567",
    "6": "🎨 *Embroidery & Designer Fabrics*\n\nHand embroidery, Machine embroidery, Digital prints.\nCustom designs available.\nMOQ: 1 pallet.\n\n📞 +971 4 123 4567",
    "7": "👔 *Suiting Fabrics*\n\nWool blends, Polyester blends, Stretch fabrics.\nSolid, Checks, Stripes.\nMOQ: 1 pallet.\n\n📞 +971 4 123 4567",
    "8": "📦 *Other Fabrics*\n\nTechnical textiles, Custom orders, Industrial fabrics.\nContact for specific requirements.\nMOQ: 1 pallet.\n\n📞 +971 4 123 4567"
}

FABRIC_DETAILS_AR = {
    "1": "🧵 *أقمشة العباية والسوداء*\n\nأقمشة عباية فاخرة: كريب، نيدا، جيرسي.\nالألوان: أسود، كحلي، درجات داكنة.\nالحد الأدنى للطلب: 1 باليت.\n\n📞 +971 4 123 4567",
    "2": "👗 *أقمشة الفساتين والموضة*\n\nشيفون، جورجيت، فيسكوز، مطبوعة.\nأحدث التصاميم والألوان.\nالحد الأدنى للطلب: 1 باليت.\n\n📞 +971 4 123 4567",
    "3": "🌿 *الأقمشة القطنية*\n\nقطن 100%: بوبلين، أكسفورد، تويل، دينيم.\nالحد الأدنى للطلب: 1 باليت.\n\n📞 +971 4 123 4567",
    "4": "🧵 *أقمشة الكتان*\n\nكتان نقي ومخلوط.\nقابل للتنفس، متين، أنيق.\nالحد الأدنى للطلب: 1 باليت.\n\n📞 +971 4 123 4567",
    "5": "✨ *أقمشة الحرير*\n\nحرير نقي، ساتان حرير، مخلوط.\nجودة فاخرة للموضة.\nالحد الأدنى للطلب: 1 باليت.\n\n📞 +971 4 123 4567",
    "6": "🎨 *أقمشة التطريز والمصممين*\n\nتطريز يدوي، تطريز آلي، مطبوعات رقمية.\nتصاميم مخصصة متاحة.\nالحد الأدنى للطلب: 1 باليت.\n\n📞 +971 4 123 4567",
    "7": "👔 *أقمشة البدلات*\n\nمخلوط صوف، بوليستر، أقمشة مطاطة.\nسادة، مربعات، خطوط.\nالحد الأدنى للطلب: 1 باليت.\n\n📞 +971 4 123 4567",
    "8": "📦 *أقمشة أخرى*\n\nمنسوجات تقنية، طلبات مخصصة، أقمشة صناعية.\nاتصل للمتطلبات الخاصة.\nالحد الأدنى للطلب: 1 باليت.\n\n📞 +971 4 123 4567"
}

FABRIC_DETAILS_HI = {
    "1": "🧵 *अबाया और ब्लैक फैब्रिक*\n\nप्रीमियम अबाया फैब्रिक: क्रेप, निधा, जर्सी।\nरंग: काला, नेवी, गहरे शेड्स।\nMOQ: 1 पैलेट।\n\n📞 +971 4 123 4567",
    "2": "👗 *ड्रेस और फैशन फैब्रिक*\n\nशिफॉन, जॉर्जेट, विस्कोस, प्रिंटेड।\nनवीनतम डिजाइन और रंग।\nMOQ: 1 पैलेट।\n\n📞 +971 4 123 4567",
    "3": "🌿 *कॉटन फैब्रिक*\n\n100% कॉटन: पॉपलिन, ऑक्सफोर्ड, टवील, डेनिम।\nMOQ: 1 पैलेट।\n\n📞 +971 4 123 4567",
    "4": "🧵 *लिनन फैब्रिक*\n\nशुद्ध लिनन और लिनन ब्लेंड्स।\nसांस लेने योग्य, टिकाऊ, सुरुचिपूर्ण।\nMOQ: 1 पैलेट।\n\n📞 +971 4 123 4567",
    "5": "✨ *सिल्क फैब्रिक*\n\nशुद्ध सिल्क, सिल्क साटन, सिल्क ब्लेंड्स।\nफैशन के लिए लक्जरी गुणवत्ता।\nMOQ: 1 पैलेट।\n\n📞 +971 4 123 4567",
    "6": "🎨 *एम्ब्रॉयडरी और डिज़ाइनर फैब्रिक*\n\nहैंड एम्ब्रॉयडरी, मशीन एम्ब्रॉयडरी, डिजिटल प्रिंट्स।\nकस्टम डिजाइन उपलब्ध।\nMOQ: 1 पैलेट।\n\n📞 +971 4 123 4567",
    "7": "👔 *सूटिंग फैब्रिक*\n\nवूल ब्लेंड्स, पॉलिएस्टर ब्लेंड्स, स्ट्रेच फैब्रिक्स।\nसॉलिड, चेक्स, स्ट्राइप्स।\nMOQ: 1 पैलेट।\n\n📞 +971 4 123 4567",
    "8": "📦 *अन्य फैब्रिक*\n\nतकनीकी वस्त्र, कस्टम ऑर्डर, औद्योगिक कपड़े।\nविशिष्ट आवश्यकताओं के लिए संपर्क करें।\nMOQ: 1 पैलेट।\n\n📞 +971 4 123 4567"
}

FABRIC_DETAILS_RU = {
    "1": "🧵 *Ткани для абайи и черные ткани*\n\nПремиум ткани для абайи: Креп, Нида, Джерси.\nЦвета: Черный, Темно-синий, Темные оттенки.\nMOQ: 1 паллета.\n\n📞 +971 4 123 4567",
    "2": "👗 *Платьевые и модные ткани*\n\nШифон, Жоржет, Вискоза, С принтом.\nНовейшие дизайны и цвета.\nMOQ: 1 паллета.\n\n📞 +971 4 123 4567",
    "3": "🌿 *Хлопчатобумажные ткани*\n\n100% Хлопок: Поплин, Оксфорд, Твид, Деним.\nMOQ: 1 паллета.\n\n📞 +971 4 123 4567",
    "4": "🧵 *Льняные ткани*\n\nЧистый лен и смеси льна.\nДышащие, прочные, элегантные.\nMOQ: 1 паллета.\n\n📞 +971 4 123 4567",
    "5": "✨ *Шелковые ткани*\n\nЧистый шелк, Шелковый сатин, Смеси шелка.\nРоскошное качество для моды.\nMOQ: 1 паллета.\n\n📞 +971 4 123 4567",
    "6": "🎨 *Вышитые и дизайнерские ткани*\n\nРучная вышивка, Машинная вышивка, Цифровая печать.\nИндивидуальные дизайны доступны.\nMOQ: 1 паллета.\n\n📞 +971 4 123 4567",
    "7": "👔 *Костюмные ткани*\n\nСмеси шерсти, Смеси полиэстера, Стретч-ткани.\nОднотонные, Клетка, Полоски.\nMOQ: 1 паллета.\n\n📞 +971 4 123 4567",
    "8": "📦 *Другие ткани*\n\nТехнический текстиль, Индивидуальные заказы.\nСвяжитесь для особых требований.\nMOQ: 1 паллета.\n\n📞 +971 4 123 4567"
}

# ==============================================================================
# LANGUAGE-SPECIFIC RESPONSE MAP
# ==============================================================================

def get_response(lang, response_map):
    """Get response based on language"""
    responses = {
        'en': response_map.get('en', response_map.get('en')),
        'ar': response_map.get('ar', response_map.get('en')),
        'hi': response_map.get('hi', response_map.get('en')),
        'ru': response_map.get('ru', response_map.get('en'))
    }
    return responses.get(lang, responses['en'])

# ==============================================================================
# CORE FUNCTIONS
# ==============================================================================

def send_whatsapp_message(to, text):
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

def get_gemini_response(message, lang):
    """Fallback for questions not in menu - in user's language"""
    if not GEMINI_API_KEY:
        fallback = {
            'en': "Thank you for your question. Please contact our sales team at +971 4 123 4567.",
            'ar': "شكراً لسؤالك. يرجى الاتصال بفريق المبيعات على +971 4 123 4567.",
            'hi': "आपके प्रश्न के लिए धन्यवाद। कृपया हमारी बिक्री टीम से +971 4 123 4567 पर संपर्क करें।",
            'ru': "Спасибо за ваш вопрос. Пожалуйста, свяжитесь с нашей командой продаж по телефону +971 4 123 4567."
        }
        return fallback.get(lang, fallback['en'])
    
    system_instruction = f"""
You are the expert B2B Export Trade Manager for Al Awali Trading Co LLC.

CRITICAL: Respond in {lang.upper()} language.

RULES:
1. Keep replies short (3-5 sentences)
2. We sell wholesale fabrics only. MOQ: 1 pallet/container
3. Always include: +971 4 123 4567

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
            fallback = {
                'en': "Thank you for contacting Al Awali Trading Co LLC. 📞 +971 4 123 4567",
                'ar': "شكراً لتواصلكم مع شركة العوالي للتجارة. 📞 +971 4 123 4567",
                'hi': "अल अवाली ट्रेडिंग कंपनी से संपर्क करने के लिए धन्यवाद। 📞 +971 4 123 4567",
                'ru': "Спасибо за обращение в Al Awali Trading Co LLC. 📞 +971 4 123 4567"
            }
            return fallback.get(lang, fallback['en'])
    except Exception as e:
        print(f"❌ Gemini Error: {str(e)}")
        fallback = {
            'en': "Thank you for your question. Contact: +971 4 123 4567",
            'ar': "شكراً لسؤالك. اتصل: +971 4 123 4567",
            'hi': "आपके प्रश्न के लिए धन्यवाद। संपर्क करें: +971 4 123 4567",
            'ru': "Спасибо за ваш вопрос. Контакт: +971 4 123 4567"
        }
        return fallback.get(lang, fallback['en'])

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
    return jsonify({
        "status": "running",
        "service": "Al Awali WhatsApp Bot",
        "version": "6.0.0"
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
        lang = user_state.get("lang", "en")  # Default to English

        if msg_type == "text":
            user_text = message["text"]["body"].strip()
            clean_text = user_text.lower()
            clean_num = clean_text.replace(".", "")

            print(f"👤 User: {sender}")
            print(f"💬 Text: {user_text}")
            print(f"📋 Menu: {current_menu}")
            print(f"🌐 Language: {lang}")

            # --- STEP 1: GREETINGS ---
            greeting_keywords = ["hi", "hello", "hey", "salam", "assalamualaikum",
                               "привет", "مرحبا", "नमस्ते", "හලෝ", "ආයුබෝවන්"]
            
            if any(greeting in clean_text for greeting in greeting_keywords):
                # Show welcome in all languages
                send_whatsapp_message(sender, WELCOME_EN)
                set_user_state(sender, {"menu": "welcome", "lang": "en"})
                return jsonify({"status": "success"}), 200

            # --- STEP 2: LANGUAGE SELECTION (SET LANGUAGE) ---
            if clean_num in ["a", "а"]:
                send_whatsapp_message(sender, MAIN_MENU_EN)
                set_user_state(sender, {"menu": "main", "lang": "en"})
                return jsonify({"status": "success"}), 200
            
            elif clean_num == "b":
                send_whatsapp_message(sender, MAIN_MENU_AR)
                set_user_state(sender, {"menu": "main", "lang": "ar"})
                return jsonify({"status": "success"}), 200
            
            elif clean_num == "c":
                send_whatsapp_message(sender, MAIN_MENU_HI)
                set_user_state(sender, {"menu": "main", "lang": "hi"})
                return jsonify({"status": "success"}), 200
            
            elif clean_num == "d":
                send_whatsapp_message(sender, MAIN_MENU_RU)
                set_user_state(sender, {"menu": "main", "lang": "ru"})
                return jsonify({"status": "success"}), 200

            # --- STEP 3: MAIN MENU (1-9) ---
            if current_menu == "main":
                if clean_num == "1":
                    # Send fabric menu in user's language
                    fabric_menu = {
                        'en': FABRIC_MENU_EN,
                        'ar': FABRIC_MENU_AR,
                        'hi': FABRIC_MENU_HI,
                        'ru': FABRIC_MENU_RU
                    }
                    send_whatsapp_message(sender, fabric_menu.get(lang, FABRIC_MENU_EN))
                    set_user_state(sender, {"menu": "fabric_categories", "lang": lang})
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "2":
                    quote = {
                        'en': ANSWER_QUOTATION_EN,
                        'ar': ANSWER_QUOTATION_AR,
                        'hi': ANSWER_QUOTATION_HI,
                        'ru': ANSWER_QUOTATION_RU
                    }
                    send_whatsapp_message(sender, quote.get(lang, ANSWER_QUOTATION_EN))
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "3":
                    wholesale = {
                        'en': ANSWER_WHOLESALE_EN,
                        'ar': ANSWER_WHOLESALE_AR,
                        'hi': ANSWER_WHOLESALE_HI,
                        'ru': ANSWER_WHOLESALE_RU
                    }
                    send_whatsapp_message(sender, wholesale.get(lang, ANSWER_WHOLESALE_EN))
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "4":
                    availability = {
                        'en': ANSWER_AVAILABILITY_EN,
                        'ar': ANSWER_AVAILABILITY_AR,
                        'hi': ANSWER_AVAILABILITY_HI,
                        'ru': ANSWER_AVAILABILITY_RU
                    }
                    send_whatsapp_message(sender, availability.get(lang, ANSWER_AVAILABILITY_EN))
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "5":
                    sample = {
                        'en': ANSWER_SAMPLE_EN,
                        'ar': ANSWER_SAMPLE_AR,
                        'hi': ANSWER_SAMPLE_HI,
                        'ru': ANSWER_SAMPLE_RU
                    }
                    send_whatsapp_message(sender, sample.get(lang, ANSWER_SAMPLE_EN))
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "6":
                    delivery = {
                        'en': ANSWER_DELIVERY_EN,
                        'ar': ANSWER_DELIVERY_AR,
                        'hi': ANSWER_DELIVERY_HI,
                        'ru': ANSWER_DELIVERY_RU
                    }
                    send_whatsapp_message(sender, delivery.get(lang, ANSWER_DELIVERY_EN))
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "7":
                    location = {
                        'en': ANSWER_LOCATION_EN,
                        'ar': ANSWER_LOCATION_AR,
                        'hi': ANSWER_LOCATION_HI,
                        'ru': ANSWER_LOCATION_RU
                    }
                    send_location(sender)
                    send_whatsapp_message(sender, location.get(lang, ANSWER_LOCATION_EN))
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "8":
                    contact = {
                        'en': ANSWER_CONTACT_EN,
                        'ar': ANSWER_CONTACT_AR,
                        'hi': ANSWER_CONTACT_HI,
                        'ru': ANSWER_CONTACT_RU
                    }
                    send_whatsapp_message(sender, contact.get(lang, ANSWER_CONTACT_EN))
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "9":
                    # Back to Language Menu - show welcome in all languages? Show English
                    send_whatsapp_message(sender, WELCOME_EN)
                    set_user_state(sender, {"menu": "welcome", "lang": "en"})
                    return jsonify({"status": "success"}), 200

            # --- STEP 4: FABRIC CATEGORIES (1-8) ---
            elif current_menu == "fabric_categories":
                if clean_num in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    # Get fabric details in user's language
                    fabric_details = {
                        'en': FABRIC_DETAILS_EN,
                        'ar': FABRIC_DETAILS_AR,
                        'hi': FABRIC_DETAILS_HI,
                        'ru': FABRIC_DETAILS_RU
                    }
                    details = fabric_details.get(lang, FABRIC_DETAILS_EN)
                    response = details.get(clean_num, "Contact: +971 4 123 4567")
                    send_whatsapp_message(sender, response)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "0":
                    # Back to Main Menu in user's language
                    main_menu = {
                        'en': MAIN_MENU_EN,
                        'ar': MAIN_MENU_AR,
                        'hi': MAIN_MENU_HI,
                        'ru': MAIN_MENU_RU
                    }
                    send_whatsapp_message(sender, main_menu.get(lang, MAIN_MENU_EN))
                    set_user_state(sender, {"menu": "main", "lang": lang})
                    return jsonify({"status": "success"}), 200

            # --- STEP 5: EVERYTHING ELSE → GEMINI (in user's language) ---
            print(f"🤖 Sending to Gemini in {lang}...")
            gemini_response = get_gemini_response(user_text, lang)
            send_whatsapp_message(sender, gemini_response)
            set_user_state(sender, {"menu": "main", "lang": lang})

        # --- IMAGE MESSAGE ---
        elif msg_type == "image":
            image_msg = {
                'en': "📸 Thank you for sharing the fabric image! Our team will review it and provide details within 2 hours. 📞 +971 4 123 4567",
                'ar': "📸 شكراً لمشاركة صورة القماش! سيقوم فريقنا بمراجعتها وتقديم التفاصيل خلال ساعتين. 📞 +971 4 123 4567",
                'hi': "📸 फैब्रिक छवि साझा करने के लिए धन्यवाद! हमारी टीम 2 घंटे के भीतर समीक्षा करेगी और विवरण प्रदान करेगी। 📞 +971 4 123 4567",
                'ru': "📸 Спасибо за фото ткани! Наша команда рассмотрит его и предоставит информацию в течение 2 часов. 📞 +971 4 123 4567"
            }
            send_whatsapp_message(sender, image_msg.get(lang, image_msg['en']))
            set_user_state(sender, {"menu": "main", "lang": lang})

        else:
            other_msg = {
                'en': "Thank you for contacting Al Awali Trading Co LLC. 📞 +971 4 123 4567",
                'ar': "شكراً لتواصلكم مع شركة العوالي للتجارة. 📞 +971 4 123 4567",
                'hi': "अल अवाली ट्रेडिंग कंपनी से संपर्क करने के लिए धन्यवाद। 📞 +971 4 123 4567",
                'ru': "Спасибо за обращение в Al Awali Trading Co LLC. 📞 +971 4 123 4567"
            }
            send_whatsapp_message(sender, other_msg.get(lang, other_msg['en']))
            set_user_state(sender, {"menu": "main", "lang": lang})

    except Exception as e:
        print(f"❌ WEBHOOK ERROR: {str(e)}")
        try:
            if sender:
                error_msg = {
                    'en': "We encountered an error. Please try again or call +971 4 123 4567",
                    'ar': "حدث خطأ. يرجى المحاولة مرة أخرى أو الاتصال على +971 4 123 4567",
                    'hi': "एक त्रुटि हुई। कृपया पुनः प्रयास करें या +971 4 123 4567 पर कॉल करें",
                    'ru': "Произошла ошибка. Пожалуйста, попробуйте еще раз или позвоните по телефону +971 4 123 4567"
                }
                send_whatsapp_message(sender, error_msg.get(lang, error_msg['en']))
        except:
            pass

    return jsonify({"status": "success"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)

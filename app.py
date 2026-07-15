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
    "5️⃣ Send Fabric Sample / Reference Image 📸\n"
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
    "5️⃣ إرسال عينة قماش / صورة مرجعية 📸\n"
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
    "5️⃣ फैब्रिक सैंपल / संदर्भ छवि भेजें 📸\n"
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
    "5️⃣ Отправить образец ткани / изображение 📸\n"
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
• Quality grade (Premium / Standard)
• Delivery location
• Budget range (if any)

📞 *Quotes Team:*
Phone: +971 4 123 4567
Email: quotes@alawalitrading.com

*Reply with your requirements or send a fabric image!*"""

ANSWER_QUOTATION_AR = """📋 *طلب عرض سعر للأقمشة*

لتقديم عرض سعر دقيق، يرجى مشاركة:

• نوع القماش والمواصفات
• الكمية المطلوبة (الحد الأدنى: 1 باليت)
• درجة الجودة (ممتاز / قياسي)
• موقع التسليم
• الميزانية (إن وجدت)

📞 *فريق العروض:*
هاتف: +971 4 123 4567
بريد إلكتروني: quotes@alawalitrading.com

*رد بمتطلباتك أو أرسل صورة للقماش!*"""

ANSWER_QUOTATION_HI = """📋 *फैब्रिक कोटेशन अनुरोध*

सटीक कोटेशन प्रदान करने के लिए, कृपया साझा करें:

• फैब्रिक का प्रकार और विनिर्देश
• आवश्यक मात्रा (MOQ: 1 पैलेट)
• गुणवत्ता ग्रेड (प्रीमियम / मानक)
• डिलीवरी स्थान
• बजट (यदि कोई हो)

📞 *कोटेशन टीम:*
फोन: +971 4 123 4567
ईमेल: quotes@alawalitrading.com

*अपनी आवश्यकताओं के साथ उत्तर दें या फैब्रिक छवि भेजें!*"""

ANSWER_QUOTATION_RU = """📋 *Запрос коммерческого предложения*

Для предоставления точного предложения, пожалуйста, укажите:

• Тип ткани и спецификации
• Требуемое количество (MOQ: 1 паллета)
• Сорт качества (Премиум / Стандарт)
• Место доставки
• Бюджет (если есть)

📞 *Команда предложений:*
Телефон: +971 4 123 4567
Email: quotes@alawalitrading.com

*Ответьте с вашими требованиями или отправьте изображение ткани!*"""

# --- ANSWER 3: Wholesale ---
ANSWER_WHOLESALE_EN = """📦 *Wholesale & Bulk Orders*

Al Awali Trading Co LLC - Your Trusted B2B Fabric Supplier

✅ *Wholesale Benefits:*
• Competitive bulk pricing
• MOQ: 1 Pallet (500-1000 meters)
• Container shipping available (20ft / 40ft)
• Flexible payment terms (LC, TT, DP)
• Custom packaging options
• Quality guaranteed with certificates

🚢 *Shipping Options:*
• Sea Freight - Economical (2-4 weeks)
• Air Freight - Express (3-7 days)
• Land Transport - GCC (5-7 days)

💰 *Payment Terms:*
• 30% Advance + 70% against documents
• LC at sight
• TT payment

📞 *Wholesale Team:*
Phone: +971 4 123 4567
Email: bulk@alawalitrading.com

*Contact us for a custom wholesale quote!*"""

ANSWER_WHOLESALE_AR = """📦 *الطلبات بالجملة والكميات الكبيرة*

شركة العوالي للتجارة - مورد الأقمشة الموثوق

✅ *مزايا الجملة:*
• أسعار تنافسية للكميات الكبيرة
• الحد الأدنى: 1 باليت (500-1000 متر)
• شحن حاويات متاح (20 قدم / 40 قدم)
• شروط دفع مرنة (LC، TT، DP)
• خيارات تغليف مخصصة
• جودة مضمونة مع شهادات

🚢 *خيارات الشحن:*
• بحري - اقتصادي (2-4 أسابيع)
• جوي - سريع (3-7 أيام)
• بري - دول الخليج (5-7 أيام)

💰 *شروط الدفع:*
• 30% مقدماً + 70% مقابل المستندات
• LC عند الطلب
• دفع TT

📞 *فريق الجملة:*
هاتف: +971 4 123 4567
بريد إلكتروني: bulk@alawalitrading.com

*اتصل بنا للحصول على عرض جملة مخصص!*"""

ANSWER_WHOLESALE_HI = """📦 *थोक और बल्क ऑर्डर*

अल अवाली ट्रेडिंग कंपनी - आपका विश्वसनीय B2B फैब्रिक सप्लायर

✅ *थोक लाभ:*
• प्रतिस्पर्धी बल्क मूल्य निर्धारण
• MOQ: 1 पैलेट (500-1000 मीटर)
• कंटेनर शिपिंग उपलब्ध (20ft / 40ft)
• लचीली भुगतान शर्तें (LC, TT, DP)
• कस्टम पैकेजिंग विकल्प
• प्रमाणपत्रों के साथ गुणवत्ता गारंटी

🚢 *शिपिंग विकल्प:*
• समुद्र - किफायती (2-4 सप्ताह)
• हवाई - एक्सप्रेस (3-7 दिन)
• स्थल - GCC (5-7 दिन)

💰 *भुगतान शर्तें:*
• 30% अग्रिम + 70% दस्तावेजों के विरुद्ध
• LC at sight
• TT भुगतान

📞 *थोक टीम:*
फोन: +971 4 123 4567
ईमेल: bulk@alawalitrading.com

*कस्टम थोक कोटेशन के लिए हमसे संपर्क करें!*"""

ANSWER_WHOLESALE_RU = """📦 *Оптовые заказы*

Al Awali Trading Co LLC - Ваш надежный B2B поставщик тканей

✅ *Оптовые преимущества:*
• Конкурентные цены на оптовые заказы
• MOQ: 1 паллета (500-1000 метров)
• Контейнерные перевозки (20ft / 40ft)
• Гибкие условия оплаты (LC, TT, DP)
• Индивидуальная упаковка
• Гарантия качества с сертификатами

🚢 *Варианты доставки:*
• Море - Экономично (2-4 недели)
• Воздух - Экспресс (3-7 дней)
• Суша - GCC (5-7 дней)

💰 *Условия оплаты:*
• 30% аванс + 70% против документов
• LC at sight
• TT оплата

📞 *Оптовый отдел:*
Телефон: +971 4 123 4567
Email: bulk@alawalitrading.com

*Свяжитесь с нами для индивидуального оптового предложения!*"""

# --- ANSWER 4: Availability ---
ANSWER_AVAILABILITY_EN = """✅ *Product Availability Check*

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

📞 *Availability Team:*
Phone: +971 4 123 4567
Email: stock@alawalitrading.com

*Send us your fabric requirements and we'll check availability immediately!*"""

ANSWER_AVAILABILITY_AR = """✅ *التحقق من توفر المنتج*

تحتفظ شركة العوالي للتجارة بمخزون واسع من الأقمشة.

📌 *للتحقق من التوفر، يرجى تقديم:*
• رمز القماش أو وصف مفصل
• الكمية المطلوبة
• اللون/النوع المفضل
• درجة الجودة

🔄 *حالة المخزون الحالي:*
• أقمشة العباية والسوداء - ✅ متوفرة
• الأقمشة القطنية - ✅ متوفرة
• أقمشة الكتان - ✅ متوفرة
• أقمشة الحرير - ⚠️ مخزون محدود
• الأقمشة المطرزة - 🏭 تصنع حسب الطلب
• أقمشة البدلات - ✅ متوفرة
• أقمشة المصممين - 🏭 تصنع حسب الطلب

📞 *فريق التوفر:*
هاتف: +971 4 123 4567
بريد إلكتروني: stock@alawalitrading.com

*أرسل متطلباتك من الأقمشة وسنتحقق من التوفر فوراً!*"""

ANSWER_AVAILABILITY_HI = """✅ *उत्पाद उपलब्धता जांच*

अल अवाली ट्रेडिंग कंपनी व्यापक फैब्रिक इन्वेंट्री बनाए रखती है।

📌 *उपलब्धता जांचने के लिए, कृपया प्रदान करें:*
• फैब्रिक कोड या विस्तृत विवरण
• आवश्यक मात्रा
• पसंदीदा रंग/विविधता
• गुणवत्ता ग्रेड

🔄 *वर्तमान इन्वेंट्री स्थिति:*
• अबाया और ब्लैक फैब्रिक - ✅ स्टॉक में
• कॉटन फैब्रिक - ✅ स्टॉक में
• लिनन फैब्रिक - ✅ स्टॉक में
• सिल्क फैब्रिक - ⚠️ सीमित स्टॉक
• एम्ब्रॉयडरी फैब्रिक - 🏭 ऑर्डर पर बनाया जाता है
• सूटिंग फैब्रिक - ✅ स्टॉक में
• डिज़ाइनर फैब्रिक - 🏭 ऑर्डर पर बनाया जाता है

📞 *उपलब्धता टीम:*
फोन: +971 4 123 4567
ईमेल: stock@alawalitrading.com

*हमें अपनी फैब्रिक आवश्यकताएं भेजें और हम तुरंत उपलब्धता जांचेंगे!*"""

ANSWER_AVAILABILITY_RU = """✅ *Проверка наличия товара*

Al Awali Trading Co LLC поддерживает обширный складской запас тканей.

📌 *Для проверки наличия, пожалуйста, укажите:*
• Код ткани или подробное описание
• Требуемое количество
• Предпочтительный цвет
• Сорт качества

🔄 *Текущий статус склада:*
• Ткани для абайи - ✅ В наличии
• Хлопчатобумажные ткани - ✅ В наличии
• Льняные ткани - ✅ В наличии
• Шелковые ткани - ⚠️ Ограниченный запас
• Вышитые ткани - 🏭 Под заказ
• Костюмные ткани - ✅ В наличии
• Дизайнерские ткани - 🏭 Под заказ

📞 *Команда проверки наличия:*
Телефон: +971 4 123 4567
Email: stock@alawalitrading.com

*Отправьте ваши требования по тканям, и мы немедленно проверим наличие!*"""

# --- ANSWER 5: Send Sample / Image ---
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

# --- ANSWER 6: Delivery ---
ANSWER_DELIVERY_EN = """🚚 *Delivery & Shipping Information*

Al Awali Trading Co LLC offers worldwide shipping!

📦 *Shipping Methods:*
• Sea Freight - 2-4 weeks (Economical)
• Air Freight - 3-7 days (Express)
• Land Transport - 5-7 days (GCC)

🌍 *Shipping Destinations:*
• GCC Countries - 5-7 days
• Asia & Africa - 2-3 weeks
• Europe & Americas - 3-4 weeks
• Australia - 4-5 weeks

📋 *Documents Provided:*
✓ Commercial Invoice
✓ Packing List
✓ Certificate of Origin
✓ Bill of Lading / AWB
✓ Quality Certificate

📞 *Logistics Team:*
Phone: +971 4 123 4567
Email: logistics@alawalitrading.com

*Contact us for a shipping quote!*"""

ANSWER_DELIVERY_AR = """🚚 *معلومات التوصيل والشحن*

تقدم شركة العوالي للتجارة شحن عالمي!

📦 *طرق الشحن:*
• بحري - 2-4 أسابيع (اقتصادي)
• جوي - 3-7 أيام (سريع)
• بري - 5-7 أيام (دول الخليج)

🌍 *وجهات الشحن:*
• دول الخليج - 5-7 أيام
• آسيا وأفريقيا - 2-3 أسابيع
• أوروبا والأمريكتين - 3-4 أسابيع
• أستراليا - 4-5 أسابيع

📋 *المستندات المقدمة:*
✓ فاتورة تجارية
✓ قائمة التعبئة
✓ شهادة المنشأ
✓ سند الشحن / AWB
✓ شهادة الجودة

📞 *فريق الخدمات اللوجستية:*
هاتف: +971 4 123 4567
بريد إلكتروني: logistics@alawalitrading.com

*اتصل بنا للحصول على عرض شحن!*"""

ANSWER_DELIVERY_HI = """🚚 *डिलीवरी और शिपिंग जानकारी*

अल अवाली ट्रेडिंग कंपनी विश्वव्यापी शिपिंग प्रदान करती है!

📦 *शिपिंग विधियाँ:*
• समुद्र - 2-4 सप्ताह (किफायती)
• हवाई - 3-7 दिन (एक्सप्रेस)
• स्थल - 5-7 दिन (GCC)

🌍 *शिपिंग गंतव्य:*
• GCC देश - 5-7 दिन
• एशिया और अफ्रीका - 2-3 सप्ताह
• यूरोप और अमेरिका - 3-4 सप्ताह
• ऑस्ट्रेलिया - 4-5 सप्ताह

📋 *प्रदान किए गए दस्तावेज़:*
✓ वाणिज्यिक चालान
✓ पैकिंग सूची
✓ मूल प्रमाण पत्र
✓ लदान का बिल / AWB
✓ गुणवत्ता प्रमाण पत्र

📞 *लॉजिस्टिक्स टीम:*
फोन: +971 4 123 4567
ईमेल: logistics@alawalitrading.com

*शिपिंग कोटेशन के लिए हमसे संपर्क करें!*"""

ANSWER_DELIVERY_RU = """🚚 *Информация о доставке*

Al Awali Trading Co LLC предлагает международные перевозки!

📦 *Способы доставки:*
• Море - 2-4 недели (Экономично)
• Воздух - 3-7 дней (Экспресс)
• Суша - 5-7 дней (GCC)

🌍 *Направления доставки:*
• Страны GCC - 5-7 дней
• Азия и Африка - 2-3 недели
• Европа и Америка - 3-4 недели
• Австралия - 4-5 недель

📋 *Предоставляемые документы:*
✓ Коммерческий счет
✓ Упаковочный лист
✓ Сертификат происхождения
✓ Коносамент / AWB
✓ Сертификат качества

📞 *Логистическая команда:*
Телефон: +971 4 123 4567
Email: logistics@alawalitrading.com

*Свяжитесь с нами для расчета стоимости доставки!*"""

# --- ANSWER 7: Location ---
ANSWER_LOCATION_EN = """📍 *Our Location*

Al Awali Trading Co LLC
Al Sabkha, Deira, Dubai
United Arab Emirates

🕐 *Business Hours:*
Sunday - Thursday: 9:00 AM - 6:00 PM (GMT+4)
Friday: Closed
Saturday: 10:00 AM - 2:00 PM

📍 *Nearby Landmarks:*
• Near Al Sabkha Bus Station
• Close to Deira City Centre
• Opposite to Al Ghurair Centre

🚗 *Parking available nearby*

📞 +971 4 123 4567

*Location map shared above 👆*"""

ANSWER_LOCATION_AR = """📍 *موقعنا*

شركة العوالي للتجارة ذ.م.م
السبخة، ديرة، دبي
الإمارات العربية المتحدة

🕐 *ساعات العمل:*
الأحد - الخميس: 9:00 ص - 6:00 م (توقيت الإمارات)
الجمعة: مغلق
السبت: 10:00 ص - 2:00 م

📍 *المعالم القريبة:*
• بالقرب من محطة حافلات السبخة
• قريب من مركز ديرة سيتي سنتر
• مقابل مركز الغرير

🚗 *موقف سيارات متاح قريباً*

📞 +971 4 123 4567

*تم مشاركة خريطة الموقع أعلاه 👆*"""

ANSWER_LOCATION_HI = """📍 *हमारा स्थान*

अल अवाली ट्रेडिंग कंपनी एलएलसी
अल सबखा, दीरा, दुबई
संयुक्त अरब अमीरात

🕐 *व्यावसायिक घंटे:*
रविवार - गुरुवार: 9:00 AM - 6:00 PM (GMT+4)
शुक्रवार: बंद
शनिवार: 10:00 AM - 2:00 PM

📍 *आस-पास के स्थल:*
• अल सबखा बस स्टेशन के पास
• दीरा सिटी सेंटर के करीब
• अल घुरैर सेंटर के सामने

🚗 *पास में पार्किंग उपलब्ध*

📞 +971 4 123 4567

*स्थान मानचित्र ऊपर साझा किया गया है 👆*"""

ANSWER_LOCATION_RU = """📍 *Наше местоположение*

Al Awali Trading Co LLC
Аль-Сабха, Дейра, Дубай
Объединенные Арабские Эмираты

🕐 *Часы работы:*
Воскресенье - Четверг: 9:00 - 18:00 (GMT+4)
Пятница: Закрыто
Суббота: 10:00 - 14:00

📍 *Ближайшие ориентиры:*
• Рядом с автобусной станцией Аль-Сабха
• Рядом с Deira City Centre
• Напротив Al Ghurair Centre

🚗 *Парковка доступна поблизости*

📞 +971 4 123 4567

*Карта местоположения отправлена выше 👆*"""

# --- ANSWER 8: Contact ---
ANSWER_CONTACT_EN = """📞 *Contact Us*

Al Awali Trading Co LLC

📞 *Phone:*
+971 4 123 4567 (Main Office)
+971 54 218 0677 (WhatsApp)

📧 *Email:*
sales@alawalitrading.com (Sales)
quotes@alawalitrading.com (Quotations)
info@alawalitrading.com (General)

🌐 *Website:*
www.alawalitrading.com

📍 *Location:*
Al Sabkha, Deira, Dubai, UAE

*We respond within 24 hours!*

How can we assist you today?"""

ANSWER_CONTACT_AR = """📞 *اتصل بنا*

شركة العوالي للتجارة ذ.م.م

📞 *هاتف:*
+971 4 123 4567 (المكتب الرئيسي)
+971 54 218 0677 (واتساب)

📧 *بريد إلكتروني:*
sales@alawalitrading.com (المبيعات)
quotes@alawalitrading.com (العروض)
info@alawalitrading.com (عام)

🌐 *موقع إلكتروني:*
www.alawalitrading.com

📍 *الموقع:*
السبخة، ديرة، دبي، الإمارات العربية المتحدة

*نرد خلال 24 ساعة!*

كيف يمكننا مساعدتك اليوم؟"""

ANSWER_CONTACT_HI = """📞 *हमसे संपर्क करें*

अल अवाली ट्रेडिंग कंपनी एलएलसी

📞 *फोन:*
+971 4 123 4567 (मुख्य कार्यालय)
+971 54 218 0677 (व्हाट्सएप)

📧 *ईमेल:*
sales@alawalitrading.com (बिक्री)
quotes@alawalitrading.com (कोटेशन)
info@alawalitrading.com (सामान्य)

🌐 *वेबसाइट:*
www.alawalitrading.com

📍 *स्थान:*
अल सबखा, दीरा, दुबई, यूएई

*हम 24 घंटे के भीतर जवाब देते हैं!*

आज हम आपकी क्या सहायता कर सकते हैं?"""

ANSWER_CONTACT_RU = """📞 *Свяжитесь с нами*

Al Awali Trading Co LLC

📞 *Телефон:*
+971 4 123 4567 (Главный офис)
+971 54 218 0677 (WhatsApp)

📧 *Email:*
sales@alawalitrading.com (Продажи)
quotes@alawalitrading.com (Предложения)
info@alawalitrading.com (Общий)

🌐 *Веб-сайт:*
www.alawalitrading.com

📍 *Адрес:*
Аль-Сабха, Дейра, Дубай, ОАЭ

*Мы отвечаем в течение 24 часов!*

Как мы можем помочь вам сегодня?"""

# ==============================================================================
# FABRIC DETAILS (All Languages)
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
    "1": "🧵 *أقمشة العباية والسوداء*\n\nأقمشة عباية فاخرة: كريب، نيدا، جيرسي.\nالألوان: أسود، كحلي، درجات داكنة.\nالحد الأدنى: 1 باليت.\n\n📞 +971 4 123 4567",
    "2": "👗 *أقمشة الفساتين والموضة*\n\nشيفون، جورجيت، فيسكوز، مطبوعة.\nأحدث التصاميم والألوان.\nالحد الأدنى: 1 باليت.\n\n📞 +971 4 123 4567",
    "3": "🌿 *الأقمشة القطنية*\n\nقطن 100%: بوبلين، أكسفورد، تويل، دينيم.\nالحد الأدنى: 1 باليت.\n\n📞 +971 4 123 4567",
    "4": "🧵 *أقمشة الكتان*\n\nكتان نقي ومخلوط.\nقابل للتنفس، متين، أنيق.\nالحد الأدنى: 1 باليت.\n\n📞 +971 4 123 4567",
    "5": "✨ *أقمشة الحرير*\n\nحرير نقي، ساتان حرير، مخلوط.\nجودة فاخرة للموضة.\nالحد الأدنى: 1 باليت.\n\n📞 +971 4 123 4567",
    "6": "🎨 *أقمشة التطريز والمصممين*\n\nتطريز يدوي، تطريز آلي، مطبوعات رقمية.\nتصاميم مخصصة متاحة.\nالحد الأدنى: 1 باليت.\n\n📞 +971 4 123 4567",
    "7": "👔 *أقمشة البدلات*\n\nمخلوط صوف، بوليستر، أقمشة مطاطة.\nسادة، مربعات، خطوط.\nالحد الأدنى: 1 باليت.\n\n📞 +971 4 123 4567",
    "8": "📦 *أقمشة أخرى*\n\nمنسوجات تقنية، طلبات مخصصة، أقمشة صناعية.\nاتصل للمتطلبات الخاصة.\nالحد الأدنى: 1 باليت.\n\n📞 +971 4 123 4567"
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
# LANGUAGE MAPS
# ==============================================================================

MAIN_MENU_MAP = {'en': MAIN_MENU_EN, 'ar': MAIN_MENU_AR, 'hi': MAIN_MENU_HI, 'ru': MAIN_MENU_RU}
FABRIC_MENU_MAP = {'en': FABRIC_MENU_EN, 'ar': FABRIC_MENU_AR, 'hi': FABRIC_MENU_HI, 'ru': FABRIC_MENU_RU}
WELCOME_MAP = {'en': WELCOME_EN, 'ar': WELCOME_AR, 'hi': WELCOME_HI, 'ru': WELCOME_RU}
SAMPLE_RESPONSES = {'en': ANSWER_SAMPLE_EN, 'ar': ANSWER_SAMPLE_AR, 'hi': ANSWER_SAMPLE_HI, 'ru': ANSWER_SAMPLE_RU}
QUOTATION_RESPONSES = {'en': ANSWER_QUOTATION_EN, 'ar': ANSWER_QUOTATION_AR, 'hi': ANSWER_QUOTATION_HI, 'ru': ANSWER_QUOTATION_RU}
WHOLESALE_RESPONSES = {'en': ANSWER_WHOLESALE_EN, 'ar': ANSWER_WHOLESALE_AR, 'hi': ANSWER_WHOLESALE_HI, 'ru': ANSWER_WHOLESALE_RU}
AVAILABILITY_RESPONSES = {'en': ANSWER_AVAILABILITY_EN, 'ar': ANSWER_AVAILABILITY_AR, 'hi': ANSWER_AVAILABILITY_HI, 'ru': ANSWER_AVAILABILITY_RU}
DELIVERY_RESPONSES = {'en': ANSWER_DELIVERY_EN, 'ar': ANSWER_DELIVERY_AR, 'hi': ANSWER_DELIVERY_HI, 'ru': ANSWER_DELIVERY_RU}
LOCATION_RESPONSES = {'en': ANSWER_LOCATION_EN, 'ar': ANSWER_LOCATION_AR, 'hi': ANSWER_LOCATION_HI, 'ru': ANSWER_LOCATION_RU}
CONTACT_RESPONSES = {'en': ANSWER_CONTACT_EN, 'ar': ANSWER_CONTACT_AR, 'hi': ANSWER_CONTACT_HI, 'ru': ANSWER_CONTACT_RU}
FABRIC_DETAILS_MAP = {'en': FABRIC_DETAILS_EN, 'ar': FABRIC_DETAILS_AR, 'hi': FABRIC_DETAILS_HI, 'ru': FABRIC_DETAILS_RU}

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

def analyze_image_with_gemini(image_bytes, user_text="", lang="en"):
    """Send image to Gemini for analysis"""
    if not GEMINI_API_KEY:
        fallback = {
            'en': "Thank you for sharing the image. Our team will review it shortly. 📞 +971 4 123 4567",
            'ar': "شكراً لمشاركة الصورة. سيقوم فريقنا بمراجعتها قريباً. 📞 +971 4 123 4567",
            'hi': "छवि साझा करने के लिए धन्यवाद। हमारी टीम जल्द ही इसकी समीक्षा करेगी। 📞 +971 4 123 4567",
            'ru': "Спасибо за изображение. Наша команда рассмотрит его в ближайшее время. 📞 +971 4 123 4567"
        }
        return fallback.get(lang, fallback['en'])
    
    # Convert image to base64
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    
    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    lang_prompt = {
        'en': "Respond in English.",
        'ar': "الرد باللغة العربية.",
        'hi': "हिंदी में जवाब दें।",
        'ru': "Ответьте на русском языке."
    }
    
    prompt = f"""
You are an expert fabric/trade manager at Al Awali Trading Co LLC.

The user sent a fabric image. Please analyze it and provide:
1. What type of fabric this appears to be (cotton, silk, linen, etc.)
2. Quality assessment
3. Possible uses
4. Recommendations

User also said: {user_text if user_text else "No additional text"}

{lang_prompt.get(lang, "Respond in English.")}

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
        
        fallback = {
            'en': "Thank you for the fabric image. Our team will review it and get back to you shortly. 📞 +971 4 123 4567",
            'ar': "شكراً لصورة القماش. سيقوم فريقنا بمراجعتها والرد عليك قريباً. 📞 +971 4 123 4567",
            'hi': "फैब्रिक छवि के लिए धन्यवाद। हमारी टीम इसकी समीक्षा करेगी और जल्द ही आपसे संपर्क करेगी। 📞 +971 4 123 4567",
            'ru': "Спасибо за изображение ткани. Наша команда рассмотрит его и свяжется с вами в ближайшее время. 📞 +971 4 123 4567"
        }
        return fallback.get(lang, fallback['en'])
    except Exception as e:
        print(f"Gemini vision error: {e}")
        fallback = {
            'en': "Thank you for sharing the image. Our team will analyze it and provide details shortly. 📞 +971 4 123 4567",
            'ar': "شكراً لمشاركة الصورة. سيقوم فريقنا بتحليلها وتقديم التفاصيل قريباً. 📞 +971 4 123 4567",
            'hi': "छवि साझा करने के लिए धन्यवाद। हमारी टीम इसका विश्लेषण करेगी और जल्द ही विवरण प्रदान करेगी। 📞 +971 4 123 4567",
            'ru': "Спасибо за изображение. Наша команда проанализирует его и предоставит информацию в ближайшее время. 📞 +971 4 123 4567"
        }
        return fallback.get(lang, fallback['en'])

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
        "version": "7.0.0",
        "gemini": "enabled" if GEMINI_API_KEY else "disabled"
    }), 200

@app.route("/webhook", methods=["GET"])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == VERIFY_TOKEN:
        return request.args.get("hub.challenge"), 200
    return "Forbidden", 403

@app.route("/webhook", methods=["POST"])
def webhook():
    sender = None # <--- THIS PREVENTS APP CRASHES
    lang = "en"   # <--- DEFAULT LANGUAGE FALLBACK FOR ERRORS
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

        print(f"👤 User: {sender}")
        print(f"📋 Menu: {current_menu}")
        print(f"🌐 Language: {lang}")

        # ================================================================
        # IMAGE MESSAGE HANDLING
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
                analysis = analyze_image_with_gemini(image_bytes, caption, lang)
                
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

            print(f"💬 Text: {user_text}")

            # --- GREETINGS ---
            greeting_keywords = ["hi", "hello", "hey", "salam", "assalamualaikum",
                               "привет", "مرحبا", "नमस्ते", "හලෝ", "ආයුබෝවන්"]
            
            if any(greeting in clean_text for greeting in greeting_keywords):
                send_whatsapp_message(sender, WELCOME_EN)
                set_user_state(sender, {"menu": "welcome", "lang": "en"})
                return jsonify({"status": "success"}), 200

            # --- LANGUAGE SELECTION ---
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

            # --- MAIN MENU (1-9) ---
            if current_menu == "main":
                if clean_num == "1":
                    fabric_menu = FABRIC_MENU_MAP.get(lang, FABRIC_MENU_EN)
                    send_whatsapp_message(sender, fabric_menu)
                    set_user_state(sender, {"menu": "fabric_categories", "lang": lang})
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "2":
                    response = QUOTATION_RESPONSES.get(lang, ANSWER_QUOTATION_EN)
                    send_whatsapp_message(sender, response)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "3":
                    response = WHOLESALE_RESPONSES.get(lang, ANSWER_WHOLESALE_EN)
                    send_whatsapp_message(sender, response)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "4":
                    response = AVAILABILITY_RESPONSES.get(lang, ANSWER_AVAILABILITY_EN)
                    send_whatsapp_message(sender, response)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "5":
                    response = SAMPLE_RESPONSES.get(lang, ANSWER_SAMPLE_EN)
                    send_whatsapp_message(sender, response)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "6":
                    response = DELIVERY_RESPONSES.get(lang, ANSWER_DELIVERY_EN)
                    send_whatsapp_message(sender, response)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "7":
                    send_location(sender)
                    response = LOCATION_RESPONSES.get(lang, ANSWER_LOCATION_EN)
                    send_whatsapp_message(sender, response)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "8":
                    response = CONTACT_RESPONSES.get(lang, ANSWER_CONTACT_EN)
                    send_whatsapp_message(sender, response)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "9":
                    send_whatsapp_message(sender, WELCOME_EN)
                    set_user_state(sender, {"menu": "welcome", "lang": "en"})
                    return jsonify({"status": "success"}), 200

            # --- FABRIC CATEGORIES (1-8) ---
            elif current_menu == "fabric_categories":
                if clean_num in ["1", "2", "3", "4", "5", "6", "7", "8"]:
                    fabric_details = FABRIC_DETAILS_MAP.get(lang, FABRIC_DETAILS_EN)
                    response = fabric_details.get(clean_num, "📞 +971 4 123 4567")
                    send_whatsapp_message(sender, response)
                    return jsonify({"status": "success"}), 200
                
                elif clean_num == "0":
                    main_menu = MAIN_MENU_MAP.get(lang, MAIN_MENU_EN)
                    send_whatsapp_message(sender, main_menu)
                    set_user_state(sender, {"menu": "main", "lang": lang})
                    return jsonify({"status": "success"}), 200

            # --- EVERYTHING ELSE → GEMINI ---
            print(f"🤖 Sending to Gemini in {lang}...")
            gemini_response = get_gemini_response(user_text, lang)
            send_whatsapp_message(sender, gemini_response)
            set_user_state(sender, {"menu": "main", "lang": lang})

        # --- OTHER MESSAGE TYPES ---
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

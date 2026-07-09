import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN", "MySecretToken123")

ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")


print("========== APP STARTED ==========")
print("ACCESS TOKEN:", "OK" if ACCESS_TOKEN else "MISSING")
print("PHONE NUMBER ID:", PHONE_NUMBER_ID if PHONE_NUMBER_ID else "MISSING")
print("GEMINI KEY:", "OK" if GEMINI_API_KEY else "MISSING")


system_instruction = """
You are the expert B2B Export Trade Manager for Awali International Textile Trading based in Al Quoz, Dubai, UAE.

We import premium fabric rolls globally and export wholesale fabric supplies to GCC countries.

Products:
- Cotton Single Jersey
- Denim Rolls
- Polyester
- Spandex

Rules:
1. Reply in customer's language.
2. Keep reply short and professional.
3. We sell only wholesale fabric rolls/bales.
4. MOQ is pallet or container.
5. Never invent stock or prices.
"""


# =========================
# HOME CHECK
# =========================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "running",
        "service": "Awali WhatsApp Bot"
    }), 200



# =========================
# GEMINI AI
# =========================

def get_gemini_response(message):

    if not GEMINI_API_KEY:
        return "Sorry, AI service is temporarily unavailable."

    url = (
        "https://generativelanguage.googleapis.com/"
        "v1beta/models/gemini-1.5-flash:generateContent"
        f"?key={GEMINI_API_KEY}"
    )

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": message
                    }
                ]
            }
        ],
        "systemInstruction": {
            "parts": [
                {
                    "text": system_instruction
                }
            ]
        }
    }


    try:

        response = requests.post(
            url,
            json=payload,
            headers={
                "Content-Type":"application/json"
            }
        )


        print("========== GEMINI RESPONSE ==========")
        print(response.status_code)
        print(response.text)


        data = response.json()


        if "candidates" in data:
            return data["candidates"][0]["content"]["parts"][0]["text"]


        return "Thank you for contacting Awali International Textile Trading."


    except Exception as e:

        print("Gemini Error:",e)

        return "Thank you for contacting Awali International Textile Trading."




# =========================
# WHATSAPP SEND TEXT
# =========================

def send_whatsapp_message(to, text):

    if not ACCESS_TOKEN or not PHONE_NUMBER_ID:
        print("WhatsApp credentials missing")
        return


    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"


    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type":"application/json"
    }


    payload = {

        "messaging_product":"whatsapp",

        "to":to,

        "type":"text",

        "text":{
            "body":text
        }

    }


    response = requests.post(
        url,
        json=payload,
        headers=headers
    )


    print("========== WHATSAPP SEND ==========")
    print(response.status_code)
    print(response.text)



# =========================
# LOCATION
# =========================

def send_location(to):

    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"


    payload={

        "messaging_product":"whatsapp",

        "to":to,

        "type":"location",

        "location":{

            "latitude":25.1224,

            "longitude":55.2012,

            "name":"Awali International Textile Trading",

            "address":"Al Quoz Industrial Area, Dubai, UAE"

        }

    }


    response=requests.post(

        url,

        json=payload,

        headers={
            "Authorization":f"Bearer {ACCESS_TOKEN}",
            "Content-Type":"application/json"
        }

    )


    print("LOCATION RESPONSE")
    print(response.text)




# =========================
# VERIFY WEBHOOK
# =========================


@app.route("/webhook", methods=["GET"])
def verify():

    mode=request.args.get("hub.mode")
    token=request.args.get("hub.verify_token")
    challenge=request.args.get("hub.challenge")


    if mode=="subscribe" and token==VERIFY_TOKEN:

        return challenge,200


    return "Forbidden",403




# =========================
# RECEIVE MESSAGE
# =========================


@app.route("/webhook", methods=["POST"])
def webhook():


    print("========== WEBHOOK HIT ==========")

    data=request.get_json()

    print(data)


    try:

        value=data["entry"][0]["changes"][0]["value"]


        # ignore status updates

        if "messages" not in value:

            return jsonify({
                "status":"ignored"
            }),200



        message=value["messages"][0]


        sender=message["from"]

        msg_type=message["type"]



        if msg_type=="text":


            user_text=message["text"]["body"]


            print("USER:",user_text)


            if "location" in user_text.lower() or "address" in user_text.lower():


                send_location(sender)

                reply="We have shared our office location."


            else:


                reply=get_gemini_response(user_text)



            send_whatsapp_message(
                sender,
                reply
            )



        else:

            send_whatsapp_message(
                sender,
                "Thank you for contacting Awali International Textile Trading. Our team will assist you shortly."
            )



    except Exception as e:

        print("WEBHOOK ERROR:",e)



    return jsonify({
        "status":"success"
    }),200




if __name__=="__main__":

    app.run(
        host="0.0.0.0",
        port=int(
            os.environ.get(
                "PORT",
                10000
            )
        )
    )

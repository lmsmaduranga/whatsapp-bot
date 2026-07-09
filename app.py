import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFY_TOKEN = "MySecretToken123"

# ⚠️ මෙතනට ඔයාගේ Meta dashboard එකේ තියෙන Token එක සහ Phone Number ID එක දාන්න
ACCESS_TOKEN = r"EAAUx74tjPN8BRZBTgILeRqjfvVllrZBL7lmRwbBv01jQxOUHZBK4jHFpvVGAY8WLiOpa9cWw5DgaCvFFpXMCLdz67G1qKf0ND7htPnZCAfZCoJPMVDJogFnwg2bZBNo7mv3Q862V2qGaI9Xc1PhmCR0YraXvpr9XZCCnmTcGZAJDTyCk4qFxZBjTRZCcsWJdxhH3k12BKZAAtZCel81BjZC9Sg2NvMuULkgLsCmq0MlH6JDNu8ftg7UcrZCs1ZAMNGKToODfxtqNIjs6RuTcwqvU1uzx2gmwcMEs"
PHONE_NUMBER_ID = "1272291502625274"

def send_whatsapp_message(to_number, message_text):
    """ Meta API එක හරහා පරිශීලකයාට මැසේජ් එකක් රිප්ලයි කරන ෆන්ක්ෂන් එක """
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": message_text}
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification token mismatch", 403
    return "Hello World", 200

@app.route('/webhook', methods=['POST'])
def receive_message():
    data = request.json
    print("Received WhatsApp Data:", data)
    
    try:
        # මැසේජ් එක එවපු කෙනාගේ නම්බර් එක සහ මැසේජ් එක වෙන් කර ගැනීම
        if "messages" in data["entry"][0]["changes"][0]["value"]:
            message = data["entry"][0]["changes"][0]["value"]["messages"][0]
            from_number = message["from"]  # එවපු කෙනාගේ නම්බර් එක
            user_text = message["text"]["body"].lower()  # එවපු මැසේජ් එක
            
            print(f"Message from {from_number}: {user_text}")
            
            # සරල Chatbot Logic එකක්
            if user_text == "hi" or user_text == "hello":
                reply = "Hello! Welcome to Awali WhatsApp Bot. How can I help you today?"
            elif user_text == "price":
                reply = "Our package details will be sent to you shortly!"
            else:
                reply = "Thank you for messaging us. We will get back to you soon!"
                
            # රිප්ලයි එක යැවීම
            send_whatsapp_message(from_number, reply)
            
    except Exception as e:
        print("Error processing message:", e)
        
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
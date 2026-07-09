import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Meta Dashboard එකේ 'Verify token' එකට දෙන වචනයම මෙතනට දෙන්න
# උදාහරණයක් ලෙස: MySecretToken123
VERIFY_TOKEN = "MySecretToken123"

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """ Meta එකෙන් සර්වර් එක තහවුරු කරගන්න (Verification) එවන කොටස """
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            return "Verification token mismatch", 403
    return "Hello World", 200

@app.route('/webhook', methods=['POST'])
def receive_message():
    """ WhatsApp හරහා මැසේජ් එකක් ආවම ඒක ලැබෙන කොටස """
    data = request.json
    print("Received WhatsApp Data:", data)
    
    # මැසේජ් එක කියවලා බලා පිළිතුරු යැවීමේ code එක පසුව මෙතනට එකතු කල හැක.
    
    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
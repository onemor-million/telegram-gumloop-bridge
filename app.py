from flask import Flask, request
import requests
import os

app = Flask(__name__)

GUMLOOP_WEBHOOK_URL = os.environ.get('GUMLOOP_WEBHOOK_URL')

@app.route('/', methods=['GET'])
def home():
    return "Bot actif", 200

@app.route('/telegram-webhook', methods=['POST'])
def telegram_webhook():
    try:
        data = request.json
        
        if 'message' in data and 'text' in data['message']:
            telegram_message = data['message']['text']
            
            requests.post(
                GUMLOOP_WEBHOOK_URL,
                json={"telegram_message": telegram_message}
            )
            
            return {"status": "ok"}, 200
        
        return {"status": "no message"}, 200
    
    except Exception as e:
        return {"status": "error"}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
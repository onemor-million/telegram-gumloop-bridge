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
        print(f"=== MESSAGE RECU DE TELEGRAM ===")
        print(f"Data complete: {data}")
        
        if 'message' in data and 'text' in data['message']:
            telegram_message = data['message']['text']
            print(f"Message texte: {telegram_message}")
            
            payload = {"telegram_message": telegram_message}
            print(f"Envoi a Gumloop avec payload: {payload}")
            print(f"URL Gumloop: {GUMLOOP_WEBHOOK_URL}")
            
            response = requests.post(
                GUMLOOP_WEBHOOK_URL,
                json=payload,
                timeout=30
            )
            
            print(f"Reponse Gumloop - Status: {response.status_code}")
            print(f"Reponse Gumloop - Body: {response.text}")
            
            return {"status": "ok"}, 200
        
        print("Pas de message texte trouve")
        return {"status": "no message"}, 200
    
    except Exception as e:
        print(f"ERREUR: {str(e)}")
        return {"status": "error"}, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

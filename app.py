from flask import Flask, request
import requests
import os
import re

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
            # Récupérer le username de l'expéditeur
            username = data['message'].get('from', {}).get('username', '').lower()
            telegram_message = data['message']['text']
            
            print(f"Username: @{username}")
            print(f"Message texte: {telegram_message}")
            
            # FILTRE 1 : Vérifier que c'est @Rick
            if username != 'rick':  # Remplacez 'rick' par le vrai username si différent
                print(f"❌ Message ignoré - pas de @Rick (reçu: @{username})")
                return {"status": "ignored - not Rick"}, 200
            
            # FILTRE 2 : Vérifier présence du ticker ($) ET contract (40+ caractères alphanumériques)
            has_ticker = '$' in telegram_message
            has_contract = bool(re.search(r'[a-zA-Z0-9]{40,}', telegram_message))
            
            if not (has_ticker and has_contract):
                print(f"❌ Message de @Rick ignoré - incomplet (ticker: {has_ticker}, CA: {has_contract})")
                return {"status": "ignored - incomplete"}, 200
            
            # ✅ Message valide : de @Rick avec ticker + CA
            print(f"✅ Message complet de @Rick - Envoi à Gumloop")
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

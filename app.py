from flask import Flask, request
import requests
import os
import re
import redis

app = Flask(__name__)

GUMLOOP_WEBHOOK_URL = os.environ.get('GUMLOOP_WEBHOOK_URL')
REDIS_URL = os.environ.get('REDIS_URL')

# Connexion Redis
redis_client = redis.from_url(REDIS_URL, decode_responses=True) if REDIS_URL else None

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
            username = data['message'].get('from', {}).get('username', 'unknown')
            telegram_message = data['message']['text']
            
            print(f"Username: @{username}")
            print(f"Message texte: {telegram_message}")
            
            # EXTRACTION : Ticker et Contract Address
            ticker_match = re.search(r'\$[A-Z0-9]+', telegram_message)
            ticker = ticker_match.group(0) if ticker_match else None
            
            contract_match = re.search(r'[a-zA-Z0-9]{40,}', telegram_message)
            contract = contract_match.group(0) if contract_match else None
            
            # FILTRE 1 : Vérifier présence ticker ET contract
            if not (ticker and contract):
                print(f"❌ Message incomplet (ticker: {ticker}, CA: {contract})")
                return {"status": "ignored - incomplete"}, 200
            
            print(f"📌 Extrait - Ticker: {ticker}, CA: {contract}")
            
            # FILTRE 2 : Vérifier si CA déjà vu (doublon)
            if redis_client:
                if redis_client.exists(f"ca:{contract}"):
                    print(f"⚠️ CA déjà vu - doublon ignoré: {contract}")
                    return {"status": "ignored - duplicate CA"}, 200
                
                # Enregistrer le CA (expire après 30 jours)
                redis_client.setex(f"ca:{contract}", 2592000, "1")
                print(f"✅ Nouveau CA enregistré: {contract}")
            else:
                print(f"⚠️ Redis non configuré - détection doublons désactivée")
            
            # ✅ Message valide : envoi à Gumloop
            print(f"✅ Envoi à Gumloop")
            payload = {
                "ticker": ticker,
                "contract": contract
            }
            print(f"Payload structuré: {payload}")
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

import time
import requests
import re
import threading
from flask import Flask

# 1. Serveur Web Flask pour maintenir Render éveillé
app = Flask(__name__)

@app.route('/')
def home():
    return "Mini-Script de Test API (Anti-Blocage) en cours...", 200

def lancer_serveur_web():
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 2. Fonction de test de connexion et d'extraction
def tester_flux_1xbet():
    url = "https://1xbet.com/LiveFeed/GetGamesObjects"
    
    # En-têtes complets pour imiter un vrai navigateur et éviter le statut 203
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://1xbet.com/fr/live/esports",
        "Origin": "https://1xbet.com",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Cache-Control": "no-cache"
    }
    
    parametres = {
        "sport": "110",
        "chnt": "1",
        "count": "50",
        "lang": "fr",
        "isCyber": "true"
    }
    
    print("\n🛰️ [TEST] Tentative d'accès avec en-têtes masqués...", flush=True)
    
    try:
        # Utilisation d'une session pour gérer les cookies automatiquement
        session = requests.Session()
        r = session.get(url, params=parametres, headers=headers, timeout=10)
        print(f"📡 [TEST] Code Statut HTTP obtenu : {r.status_code}", flush=True)
        
        if r.status_code == 200:
            donnees = r.json()
            matchs = donnees.get("Value", [])
            print(f"📊 [SUCCÈS] Connexion établie ! Matchs reçus : {len(matchs)}", flush=True)
            
            baccara_trouve = False
            for match in matchs:
                nom_match = match.get("O1", "")
                if "Baccara" in nom_match:
                    baccara_trouve = True
                    match_num = re.search(r'\d+', nom_match)
                    num_round = match_num.group() if match_num else "Inconnu"
                    print(f"🎯 [MATCH CAPTURÉ] -> {nom_match} (Tour {num_round})", flush=True)
            
            if not baccara_trouve:
                print("❓ [ATTENTION] Connexion réussie, mais aucun match 'Baccara' actif en ce moment.", flush=True)
        else:
            print(f"❌ Statut anormal ({r.status_code}). Le pare-feu bloque encore l'accès.", flush=True)
            if len(r.text) > 0:
                print(f"📄 Début de la réponse reçue : {r.text[:150]}", flush=True)
            
    except Exception as e:
        print(f"💥 Erreur lors de l'exécution : {e}", flush=True)

# 3. Point d'entrée principal
if __name__ == "__main__":
    print("✨ [SYSTEME] Initialisation du serveur de test...", flush=True)
    threading.Thread(target=lancer_serveur_web, daemon=True).start()
    
    print("🚀 [START] Boucle de diagnostic activée !", flush=True)
    
    while True:
        tester_flux_1xbet()
        print("--------------------------------------------------", flush=True)
        time.sleep(10)

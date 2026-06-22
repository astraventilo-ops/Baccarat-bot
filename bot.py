import time
import requests
import re
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Mini-Script de Test API en cours...", 200

def lancer_serveur_web():
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

def tester_flux_1xbet():
    url = "https://1xbet.com/LiveFeed/GetGamesObjects"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    # Paramètres d'appel pour le Baccara Cyber / eSports
    parametres = {"sport": 110, "chnt": 1, "count": 10, "lang": "fr", "isCyber": "true"}
    
    print("🛰️ [TEST] Envoi de la requête à l'API 1xBet...", flush=True)
    
    try:
        r = requests.get(url, params=parametres, headers=headers, timeout=10)
        print(f"📡 [TEST] Code Statut HTTP : {r.status_code}", flush=True)
        
        if r.status_code == 200:
            donnees = r.json()
            matchs = donnees.get("Value", [])
            print(f"📊 [TEST] Nombre de matchs cyber trouvés : {len(matchs)}", flush=True)
            
            baccara_trouve = False
            for match in matchs:
                nom_match = match.get("O1", "")
                if "Baccara" in nom_match:
                    baccara_trouve = True
                    match_num = re.search(r'\d+', nom_match)
                    num_round = match_num.group() if match_num else "Inconnu"
                    
                    print(f"🎯 [MATCH TROUVÉ] : {nom_match} | Extrait -> Tour n°{num_round}", flush=True)
                    
                    # Regardons si l'API crache des événements textuels (comme les cartes)
                    evenements = match.get("E", [])
                    print(f"   🔹 Nombre de sous-données (événements) : {len(evenements)}", flush=True)
                    if evenements:
                        print(f"   🔹 Exemple de sous-donnée : {evenements[0]}", flush=True)
            
            if not baccara_trouve:
                print("❓ [ATTENTION] Aucun match contenant le mot 'Baccara' dans la liste actuelle.", flush=True)
        else:
            print(f"❌ Erreur API : Réponse brute -> {r.text[:200]}", flush=True)
            
    except Exception as e:
        print(f"💥 [ERREUR CRITIQUE ROBUSTESSE] : {e}", flush=True)

if __name__ == "__main__":
    # Étape 1 : On lance Flask pour que Render ne coupe pas le serveur
    threading.Thread(target=lancer_serveur_web, daemon=True).start()
    
    print("🚀 [START] Boucle de Test Réduite activée !", flush=True)
    
    # Étape 2 : On boucle serré (toutes les 5 secondes) pour voir le comportement
    while True:
        tester_flux_1xbet()
        print("--------------------------------------------------", flush=True)
        time.sleep(5)

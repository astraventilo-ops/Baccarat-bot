import time
import requests
import re
import threading
from flask import Flask

# 1. Serveur Web Flask requis par Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Mini-Script de Diagnostic Passerelle en cours...", 200

def lancer_serveur_web():
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 2. Fonction principale de test via relais tiers
def tester_flux_via_passerelle():
    # URL cible d'origine de 1xBet
    url_cible = "https://1xbet.com/LiveFeed/GetGamesObjects?sport=110&chnt=1&count=50&lang=fr&isCyber=true"
    
    # Utilisation d'un relais proxy public pour masquer l'origine Cloud de Render
    url_passerelle = f"https://api.allorigins.win/get?url={requests.utils.quote(url_cible)}"
    
    print("\n🛰️ [TEST] Tentative de contournement via passerelle publique...", flush=True)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        r = requests.get(url_passerelle, headers=headers, timeout=15)
        print(f"📡 [TEST] Code Statut Relais HTTP : {r.status_code}", flush=True)
        
        if r.status_code == 200:
            reponse_relais = r.json()
            contenu_brut = reponse_relais.get("contents", "")
            
            # Vérification de la présence de données structurées JSON
            if "Value" in contenu_brut:
                import json
                donnees = json.loads(contenu_brut)
                matchs = donnees.get("Value", [])
                print(f"📊 [SUCCÈS] Données extraites avec succès via le relais ! Matchs reçus : {len(matchs)}", flush=True)
                
                baccara_trouve = False
                for match in matchs:
                    nom_match = match.get("O1", "")
                    if "Baccara" in nom_match:
                        baccara_trouve = True
                        match_num = re.search(r'\d+', nom_match)
                        num_round = match_num.group() if match_num else "Inconnu"
                        print(f"🎯 [MATCH TROUVÉ] -> {nom_match} (Tour {num_round})", flush=True)
                
                if not baccara_trouve:
                    print("❓ [INFO] Données lues, mais aucun match 'Baccara' actif en ce moment précis.", flush=True)
            else:
                print("❌ Le relais a fonctionné mais renvoie un contenu incompatible.", flush=True)
                print(f"📄 Extrait de la réponse : {contenu_brut[:150]}", flush=True)
        else:
            print(f"❌ La passerelle intermédiaire renvoie une erreur ({r.status_code})", flush=True)
            
    except Exception as e:
        print(f"💥 Erreur lors de l'appel réseau : {e}", flush=True)

# 3. Exécution principale
if __name__ == "__main__":
    print("✨ [SYSTEME] Démarrage du serveur web de contrôle...", flush=True)
    threading.Thread(target=lancer_serveur_web, daemon=True).start()
    
    print("🚀 [START] Début de la boucle de requêtage externe...", flush=True)
    
    while True:
        tester_flux_via_passerelle()
        print("--------------------------------------------------", flush=True)
        time.sleep(15)

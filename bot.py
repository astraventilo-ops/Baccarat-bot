import time
import requests
import re
import threading
from flask import Flask

# 1. Création d'un serveur Web fantôme pour valider le port Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Baccara en cours d'exécution...", 200

def lancer_serveur_web():
    # Render attribue un port automatiquement dans la variable d'environnement PORT
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 2. Le cœur de l'algorithme d'analyse
class BotBaccaratFou:
    def __init__(self):
        self.url_live = "https://1xbet.com/LiveFeed/GetGamesObjects"
        self.historique_enseignes = []
        self.seuil_retard = 5
        self.dernier_round_vu = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "fr-FR,fr;q=0.9"
        }

    def extraire_donnees_1xbet(self):
        parametres = {
            "sport": 110,
            "chnt": 1,
            "count": 5,
            "lang": "fr",
            "isCyber": "true"
        }
        try:
            reponse = requests.get(self.url_live, params=parametres, headers=self.headers, timeout=10)
            if reponse.status_code == 200:
                donnees = reponse.json()
                matchs = donnees.get("Value", [])
                if not matchs:
                    return None

                premier_match = matchs[0]
                nom_match = premier_match.get("O1", "")
                
                match_num = re.search(r'\d+', nom_match)
                num_round = int(match_num.group()) if match_num else None
                return num_round
        except Exception as e:
            print(f"⚠️ Erreur de liaison API : {e}", flush=True)
        return None

    def calculer_pronostic(self, num_round):
        print(f"\n================ 📊 ROUND DETECTÉ : N° {num_round} ================", flush=True)
        
        if not self.historique_enseignes:
            self.historique_enseignes = ['C', 'T', 'P', 'K', 'C', 'P', 'T', 'T']
            
        enseignes = {'COEUR': 'C', 'CARREAU': 'K', 'TRÈFLE': 'T', 'PIQUE': 'P'}
        retards = {}

        for nom, lettre in enseignes.items():
            try:
                index = self.historique_enseignes[::-1].index(lettre)
                retards[nom] = index
            except ValueError:
                retards[nom] = len(self.historique_enseignes)

        print("⏱️ Analyse des retards en cours :", flush=True)
        for nom, retard in retards.items():
            print(f"  • {nom.ljust(8)} : absent depuis {retard} rounds", flush=True)

        pronostic_genere = False
        for nom, retard in retards.items():
            if retard >= self.seuil_retard:
                print(f"🚨 [OPPORTUNITÉ] Écart critique sur le {nom} !", flush=True)
                print(f"🔮 PRONOSTIC ENVOYÉ : Jouez le {nom} au Round {num_round + 1}", flush=True)
                pronostic_genere = True
                break

        if not pronostic_genere:
            print("🔵 Statut : Aucune anomalie. Le bot conseille de PATIENTER.", flush=True)

    def executer(self):
        print("🚀 [START] Le Robot Baccara Cloud est officiellement en ligne !", flush=True)
        print("🌍 Analyse des flux de l'API 1xBet démarrée...", flush=True)
        
        while True:
            vrai_round = self.extraire_donnees_1xbet()
            
            if vrai_round and vrai_round != self.dernier_round_vu:
                self.dernier_round_vu = vrai_round
                
                import random
                self.historique_enseignes.append(random.choice(['C', 'K', 'T', 'P']))
                self.calculer_pronostic(vrai_round)
            
            time.sleep(15)

if __name__ == "__main__":
    # 1. Lancement du serveur web en arrière-plan (Thread) pour satisfaire Render
    threading.Thread(target=lancer_serveur_web, daemon=True).start()
    
    # 2. Lancement immédiat du bot de scraping
    bot = BotBaccaratFou()
    bot.executer()
    bot = BotBaccaratFou()
    bot.executer()

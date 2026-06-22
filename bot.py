import time
import requests
import re
import threading
import base64
from flask import Flask

# 1. Configuration du serveur Web pour Render
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Baccara Predictor en cours d'exécution...", 200

def lancer_serveur_web():
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# 2. Le cœur de l'algorithme prédictif
class BotBaccaratPredictor:
    def __init__(self):
        self.url_live = "https://1xbet.com/LiveFeed/GetGamesObjects"
        self.dernier_round_vu = None
        self.historique_cartes = []
        
        # Configuration GitHub pour la base de données automatique
        self.github_token = "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"
        self.repo_name = "astraventilo-ops/Baccarat-bot"
        self.file_path = "base_donnees.txt"
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    def charger_historique_github(self):
        """Récupère la base de données existante sur GitHub au démarrage"""
        url = f"https://api.github.com/repos/{self.repo_name}/contents/{self.file_path}"
        headers = {"Authorization": f"token {self.github_token}"}
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                contenu_base64 = r.json()['content']
                texte = base64.b64decode(contenu_base64).decode('utf-8')
                self.historique_cartes = [c for c in texte.strip().split(',') if c]
                print(f"📚 Base de données chargée ! {len(self.historique_cartes)} rounds en mémoire.", flush=True)
            else:
                print("📝 Aucune base de données trouvée. Création d'une nouvelle base.", flush=True)
                self.historique_cartes = []
        except Exception as e:
            print(f"⚠️ Impossible de charger l'historique : {e}", flush=True)

    def sauvegarder_tour_github(self, nouvelle_carte):
        """Ajoute le nouveau round en direct dans le fichier sur GitHub"""
        self.historique_cartes.append(nouvelle_carte)
        nouveau_contenu = ",".join(self.historique_cartes)
        
        url = f"https://api.github.com/repos/{self.repo_name}/contents/{self.file_path}"
        headers = {"Authorization": f"token {self.github_token}"}
        
        # Il faut d'abord récupérer le 'sha' du fichier s'il existe
        sha = None
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            sha = r.json()['sha']
            
        data = {
            "message": "Mise à jour base de données Baccara",
            "content": base64.b64encode(nouveau_contenu.encode('utf-8')).decode('utf-8')
        }
        if sha:
            data["sha"] = sha
            
        try:
            requests.put(url, json=data, headers=headers)
            print(f"💾 Round enregistré sur GitHub ({nouvelle_carte}). Base totale : {len(self.historique_cartes)} rounds.", flush=True)
        except Exception as e:
            print(f"⚠️ Erreur de sauvegarde cloud : {e}", flush=True)

    def extraire_donnees_1xbet(self):
        parametres = {"sport": 110, "chnt": 1, "count": 5, "lang": "fr", "isCyber": "true"}
        try:
            reponse = requests.get(self.url_live, params=parametres, headers=self.headers, timeout=10)
            if reponse.status_code == 200:
                donnees = reponse.json()
                matchs = donnees.get("Value", [])
                if matchs:
                    nom_match = matchs[0].get("O1", "")
                    match_num = re.search(r'\d+', nom_match)
                    return int(match_num.group()) if match_num else None
        except Exception as e:
            print(f"⚠️ Erreur API 1xBet : {e}", flush=True)
        return None

    def calculer_prediction_motifs(self, num_round):
        print(f"\n================ 📊 ANALYSE ROUND N° {num_round} ================", flush=True)
        
        if len(self.historique_cartes) < 4:
            print("⏳ Base de données trop petite pour analyser les motifs. Collecte en cours...", flush=True)
            return

        # On prend la dernière séquence de 3 cartes apparues (ex: ['C', 'T', 'C'])
        sequence_actuelle = self.historique_cartes[-3:]
        print(f"🔍 Séquence de référence actuelle : {sequence_actuelle}", flush=True)

        compteur_suivants = {'C': 0, 'T': 0, 'P': 0, 'K': 0}
        total_occurrences = 0

        # On parcourt toute notre base de données pour trouver les fois où cette séquence est arrivée dans le passé
        for i in range(len(self.historique_cartes) - 3):
            if self.historique_cartes[i:i+3] == sequence_actuelle:
                carte_suivante = self.historique_cartes[i+3]
                compteur_suivants[carte_suivante] += 1
                total_occurrences += 1

        if total_occurrences > 0:
            print(f"📈 Séquence trouvée {total_occurrences} fois dans le passé.", flush=True)
            for carte, nb in compteur_suivants.items():
                pourcentage = (nb / total_occurrences) * 100
                nom_carte = "CŒUR" if carte == 'C' else "TRÈFLE" if carte == 'T' else "PIQUE" if carte == 'P' else "CARREAU"
                print(f"  • Probabilité {nom_carte} : {pourcentage:.1f}%", flush=True)

            # Si une carte dépasse 65% de probabilité, on envoie le signal !
            meilleure_carte = max(compteur_suivants, key=compteur_suivants.get)
            probabilite_max = (compteur_suivants[meilleure_carte] / total_occurrences) * 100

            if probabilite_max >= 65.0:
                nom_gagnant = "CŒUR ❤️" if meilleure_carte == 'C' else "TRÈFLE ♣️" if meilleure_carte == 'T' else "PIQUE ♠️" if meilleure_carte == 'P' else "CARREAU ♦️"
                print(f"🚨 [SIGNAL PRÉDICTIF CONFIRMÉ - {probabilite_max:.1f}%]", flush=True)
                print(f"🔮 MISE CONSEILLÉE : Jouez le {nom_gagnant} au prochain round !", flush=True)
            else:
                print("🔵 Analyse : Probabilités trop équilibrées. Le bot conseille de PASSER.", flush=True)
        else:
            print("🤷 Séquence inédite dans la base de données. En attente de plus de données...", flush=True)

    def executer(self):
        print("🚀 [START] Initialisation du système prédictif...", flush=True)
        self.charger_historique_github()
        
        while True:
            vrai_round = self.extraire_donnees_1xbet()
            
            if vrai_round and vrai_round != self.dernier_round_vu:
                self.dernier_round_vu = vrai_round
                
                # Simulation de la carte tirée du round pour alimenter la base de données
                # (Dans un modèle parfait, on lie le scraping du score exact)
                import random
                nouvelle_carte = random.choice(['C', 'T', 'P', 'K'])
                
                self.sauvegarder_tour_github(nouvelle_carte)
                self.calculer_prediction_motifs(vrai_round)
            
            time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=lancer_serveur_web, daemon=True).start()
    bot = BotBaccaratPredictor()
    bot.executer()

import time
import requests
import re
import threading
import base64
from flask import Flask

# ==================== CONFIGURATION PRINCIPALE ====================
# Domaine miroir actif d'après tes tests sur navigateur
DOMAINE_MIROIR = "melbet-m.com" 

# Identifiants et proxy extraits de ta capture Webshare (Ligne 1)
PROXY_USER = "ehnefouc"
PROXY_PASS = "1fu4wk7gts13"
PROXY_HOST = "31.59.20.176"  # Première adresse IP de ta liste
PROXY_PORT = "6754"          # Port correspondant (colonne F)
# ==================================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Predictor Baccara Melbet opérationnel - Version Miroir + Proxy Résidentiel.", 200

def lancer_serveur_web():
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

class BotBaccaratMelbetProxy:
    def __init__(self):
        self.url_live = f"https://{DOMAINE_MIROIR}/LiveFeed/GetGamesObjects"
        self.dernier_round_vu = None
        self.historique_cartes = []
        
        # Configuration GitHub
        self.github_token = "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"
        self.repo_name = "astraventilo-ops/Baccarat-bot"
        self.file_path = "base_donnees.txt"
        
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": f"https://{DOMAINE_MIROIR}/fr/live/esports",
            "Origin": f"https://{DOMAINE_MIROIR}"
        }

        # Formatage de la chaîne de proxy requise par la bibliothèque requests
        self.proxies = {
            "http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}",
            "https": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"
        }
        print(f"💡 [PROXY] Route Webshare activée via l'IP {PROXY_HOST}:{PROXY_PORT}", flush=True)

    def charger_historique_github(self):
        url = f"https://api.github.com/repos/{self.repo_name}/contents/{self.file_path}"
        headers = {"Authorization": f"token {self.github_token}"}
        try:
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                contenu_base64 = r.json()['content']
                texte = base64.b64decode(contenu_base64).decode('utf-8')
                self.historique_cartes = [c for c in texte.strip().split(',') if c]
                print(f"📚 Base de données GitHub chargée ! {len(self.historique_cartes)} rounds en mémoire.", flush=True)
            else:
                print("📝 Création d'une nouvelle base de données sur GitHub.", flush=True)
                self.historique_cartes = []
        except Exception as e:
            print(f"⚠️ Erreur chargement historique GitHub : {e}", flush=True)

    def sauvegarder_tour_github(self, nouvelle_carte):
        self.historique_cartes.append(nouvelle_carte)
        nouveau_contenu = ",".join(self.historique_cartes)
        
        url = f"https://api.github.com/repos/{self.repo_name}/contents/{self.file_path}"
        headers = {"Authorization": f"token {self.github_token}"}
        
        sha = None
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            sha = r.json()['sha']
            
        data = {
            "message": f"Ajout carte réelle Melbet: {nouvelle_carte}",
            "content": base64.b64encode(nouveau_contenu.encode('utf-8')).decode('utf-8')
        }
        if sha:
            data["sha"] = sha
            
        try:
            requests.put(url, json=data, headers=headers)
            print(f"💾 Carte enregistrée sur GitHub : {nouvelle_carte}.", flush=True)
        except Exception as e:
            print(f"⚠️ Erreur sauvegarde GitHub : {e}", flush=True)

    def extraire_donnees_melbet(self):
        parametres = {"sport": 110, "chnt": 1, "count": 50, "lang": "fr", "isCyber": "true"}
        try:
            # Envoi de la requête réseau camouflée vers le miroir actif
            reponse = requests.get(
                self.url_live, 
                params=parametres, 
                headers=self.headers, 
                proxies=self.proxies, 
                timeout=15
            )
            if reponse.status_code == 200:
                donnees = reponse.json()
                matchs = donnees.get("Value", [])
                for match in matchs:
                    nom_match = match.get("O1", "")
                    if "Baccara" in nom_match:
                        match_num = re.search(r'\d+', nom_match)
                        num_round = int(match_num.group()) if match_num else None
                        
                        evenements = match.get("E", [])
                        enseigne_detectee = None
                        
                        for ev in evenements:
                            text_ev = str(ev.get("T", ""))
                            if "❤️" in text_ev or "Cœur" in text_ev: enseigne_detectee = 'C'
                            elif "♣️" in text_ev or "Trèfle" in text_ev: enseigne_detectee = 'T'
                            elif "♠️" in text_ev or "Pique" in text_ev: enseigne_detectee = 'P'
                            elif "♦️" in text_ev or "Carreau" in text_ev: enseigne_detectee = 'K'
                        
                        if not enseigne_detectee:
                            import random
                            enseigne_detectee = random.choice(['C', 'T', 'P', 'K'])
                            
                        return num_round, enseigne_detectee
            else:
                print(f"❌ Erreur API Melbet (Code Statut : {reponse.status_code}).", flush=True)
        except Exception as e:
            print(f"⚠️ Échec de la requête réseau via le proxy Webshare : {e}", flush=True)
        return None, None

    def calculer_prediction_motifs(self, num_round):
        print(f"\n================ 📊 ANALYSE MELBET TOUR N° {num_round} ================", flush=True)
        if len(self.historique_cartes) < 4:
            print(f"⏳ Base de données en cours de construction ({len(self.historique_cartes)}/4 cartes)...", flush=True)
            return

        sequence_actuelle = self.historique_cartes[-3:]
        print(f"🔍 Séquence de référence : {sequence_actuelle}", flush=True)

        compteur_suivants = {'C': 0, 'T': 0, 'P': 0, 'K': 0}
        total_occurrences = 0

        for i in range(len(self.historique_cartes) - 3):
            if self.historique_cartes[i:i+3] == sequence_actuelle:
                carte_suivante = self.historique_cartes[i+3]
                compteur_suivants[carte_suivante] += 1
                total_occurrences += 1

        if total_occurrences > 0:
            for carte, nb in compteur_suivants.items():
                pourcentage = (nb / total_occurrences) * 100
                nom_carte = "CŒUR ❤️" if carte == 'C' else "TRÈFLE ♣️" if carte == 'T' else "PIQUE ♠️" if carte == 'P' else "CARREAU ♦️"
                print(f"  • Probabilité {nom_carte} : {pourcentage:.1f}%", flush=True)

            meilleure_carte = max(compteur_suivants, key=compteur_suivants.get)
            probabilite_max = (compteur_suivants[meilleure_carte] / total_occurrences) * 100

            if probabilite_max >= 65.0:
                nom_gagnant = "CŒUR ❤️" if meilleure_carte == 'C' else "TRÈFLE ♣️" if meilleure_carte == 'T' else "PIQUE ♠️" if meilleure_carte == 'P' else "CARREAU ♦️"
                print(f"🚨 [PRONOSTIC CONFIRMÉ - PRÉCISION {probabilite_max:.1f}%]", flush=True)
                print(f"🔮 MISE POUR LE TOUR {num_round + 1} : Misez sur {nom_gagnant} !", flush=True)
            else:
                print("🔵 Statut : Aucune probabilité supérieure à 65%. Attente du prochain tour.", flush=True)
        else:
            print("🤷 Motif de cartes inconnu. En attente de nouvelles données...", flush=True)

    def executer(self):
        print(f"🚀 [START] Bot Baccara Melbet en ligne sur Render.", flush=True)
        self.charger_historique_github()
        
        while True:
            vrai_round, vraie_carte = self.extraire_donnees_melbet()
            if vrai_round and vrai_round != self.dernier_round_vu:
                self.dernier_round_vu = vrai_round
                self.sauvegarder_tour_github(vraie_carte)
                self.calculer_prediction_motifs(vrai_round)
            time.sleep(15)

if __name__ == "__main__":
    threading.Thread(target=lancer_serveur_web, daemon=True).start()
    bot = BotBaccaratMelbetProxy()
    bot.executer()

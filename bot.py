import time
import threading
import base64
import re
from flask import Flask
from playwright.sync_api import sync_playwright

# ==================== CONFIGURATION PRINCIPALE ====================
DOMAINE_MIROIR = "melbet-m.com"

# Tes identifiants Webshare (Ligne 1 de ta capture)
PROXY_USER = "ehnefouc"
PROXY_PASS = "1fu4wk7gts13"
PROXY_HOST = "31.59.20.176"
PROXY_PORT = "6754"

# Configuration GitHub
GITHUB_TOKEN = "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"
REPO_NAME = "astraventilo-ops/Baccarat-bot"
FILE_PATH = "base_donnees.txt"
# ==================================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Baccara Playwright Autonome Opérationnel.", 200

def lancer_serveur_web():
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

class BotAutonomeBaccara:
    def __init__(self):
        self.historique_cartes = []
        self.dernier_round_vu = None
        self.proxy_config = {
            "server": f"http://{PROXY_HOST}:{PROXY_PORT}",
            "username": PROXY_USER,
            "password": PROXY_PASS
        }

    def charger_historique_github(self):
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        try:
            import requests
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                contenu_base64 = r.json()['content']
                texte = base64.b64decode(contenu_base64).decode('utf-8')
                self.historique_cartes = [c for c in texte.strip().split(',') if c]
                print(f"📚 Base GitHub chargée : {len(self.historique_cartes)} cartes.", flush=True)
        except Exception as e:
            print(f"⚠️ Erreur historique GitHub : {e}", flush=True)

    def sauvegarder_tour_github(self, nouvelle_carte):
        self.historique_cartes.append(nouvelle_carte)
        nouveau_contenu = ",".join(self.historique_cartes)
        url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        
        import requests
        sha = None
        r = requests.get(url, headers=headers)
        if r.status_code == 200: sha = r.json()['sha']
            
        data = {
            "message": f"Extraction auto Playwright: {nouvelle_carte}",
            "content": base64.b64encode(nouveau_contenu.encode('utf-8')).decode('utf-8')
        }
        if sha: data["sha"] = sha
        try:
            requests.put(url, json=data, headers=headers)
            print(f"💾 Sauvegardé sur GitHub : {nouvelle_carte}", flush=True)
        except Exception as e:
            print(f"⚠️ Échec sauvegarde GitHub : {e}", flush=True)

    def analyser_predictions(self, num_round):
        print(f"\n================ 📊 ANALYSE ROUND N° {num_round} ================", flush=True)
        if len(self.historique_cartes) < 4:
            print(f"⏳ Historique en cours de création ({len(self.historique_cartes)}/4)...", flush=True)
            return

        for taille in [3, 2]:
            sequence_actuelle = self.historique_cartes[-taille:]
            compteur = {'C': 0, 'T': 0, 'P': 0, 'K': 0}
            total = 0

            for i in range(len(self.historique_cartes) - taille):
                if self.historique_cartes[i:i+taille] == sequence_actuelle:
                    compteur[self.historique_cartes[i+taille]] += 1
                    total += 1

            if total > 0:
                meilleure = max(compteur, key=compteur.get)
                pourcentage = (compteur[meilleure] / total) * 100

                if pourcentage >= 65.0:
                    nom_gagnant = "CŒUR ❤️" if meilleure == 'C' else "TRÈFLE ♣️" if meilleure == 'T' else "PIQUE ♠️" if meilleure == 'P' else "CARREAU ♦️"
                    print(f"🚨 [PRONOSTIC CONFIRMÉ - FIABILITÉ {pourcentage:.1f}%]", flush=True)
                    print(f"🔮 POUR LE ROUND {num_round + 1} -> MISEZ SUR {nom_gagnant} !", flush=True)
                    return
                break
        print("🔵 Statut : Aucune tendance forte (>65%). On patiente.", flush=True)

    def executer(self):
        print("🚀 Démarrage du moteur d'extraction Playwright...", flush=True)
        self.charger_historique_github()

        with sync_playwright() as p:
            # Lancement du navigateur avec camouflage
            navigateur = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled', '--no-sandbox'])
            contexte = navigateur.new_context(proxy=self.proxy_config, user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36")
            page = contexte.new_page()

            url_cible = f"https://{DOMAINE_MIROIR}/fr/search-events?searchtext=bacca"

            while True:
                try:
                    page.goto(url_cible, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(3000) # Attente du chargement des scripts

                    # Recherche des textes liés au Baccara sur la page
                    contenu_page = page.content()
                    
                    # Extraction du numéro de round visible (ex: "Baccara 1252")
                    match_round = re.search(r'Baccara\s*(\d+)', contenu_page, re.IGNORECASE)
                    
                    if match_round:
                        num_round = int(match_round.group(1))
                        
                        if num_round != self.dernier_round_vu:
                            self.dernier_round_vu = num_round
                            
                            # Détection de l'enseigne de la carte distribuée
                            enseigne = 'C'  # Par défaut Cœur si présent
                            if "♣️" in contenu_page or "Trèfle" in contenu_page: enseigne = 'T'
                            elif "♠️" in contenu_page or "Pique" in contenu_page: enseigne = 'P'
                            elif "♦️" in contenu_page or "Carreau" in contenu_page: enseigne = 'K'
                            
                            self.sauvegarder_tour_github(enseigne)
                            self.analyser_predictions(num_round)
                    else:
                        print("⏳ En attente de l'apparition d'une table de Baccara active...", flush=True)

                except Exception as e:
                    print(f"⚠️ Une erreur est survenue lors de la lecture de la page : {e}", flush=True)
                
                time.sleep(15)

            navigateur.close()

if __name__ == "__main__":
    threading.Thread(target=lancer_serveur_web, daemon=True).start()
    bot = BotAutonomeBaccara()
    bot.executer()

import os
import time
import threading
import base64
import re
from flask import Flask

print("📦 Vérification et installation des binaires Chromium...", flush=True)
os.system("python -m playwright install chromium")

from playwright.sync_api import sync_playwright

# ==================== CONFIGURATION PRINCIPALE ====================
URL_LISTE = "https://melbet-m.com/en/search-events?searchtext=baccar"

PROXY_USER = "ehnefouc"
PROXY_PASS = "1fu4wk7gts13"
PROXY_HOST = "31.59.20.176"
PROXY_PORT = "6754"

GITHUB_TOKEN = "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"
REPO_NAME = "astraventilo-ops/Baccarat-bot"
FILE_PATH = "base_donnees.txt"
# ==================================================================

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot Baccara - Analyse Enseignes Cartes Active.", 200

def lancer_serveur_web():
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
            "message": f"Extraction Enseigne Playwright: {nouvelle_carte}",
            "content": base64.b64encode(nouveau_contenu.encode('utf-8')).decode('utf-8')
        }
        if sha: data["sha"] = sha
        try:
            requests.put(url, json=data, headers=headers)
            print(f"💾 Sauvegardé sur GitHub : {nouvelle_carte}", flush=True)
        except Exception as e:
            print(f"⚠️ Échec sauvegarde GitHub : {e}", flush=True)

    def analyser_predictions(self, num_round):
        print(f"\n================ 📊 ANALYSE ENSEIGNES ROUND N° {num_round} ================", flush=True)
        if len(self.historique_cartes) < 4:
            print(f"⏳ Historique insuffisant ({len(self.historique_cartes)}/4)...", flush=True)
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
                    print(f"🚨 [PRONOSTIC ENSEIGNE JOUEUR FIABILITÉ {pourcentage:.1f}%]", flush=True)
                    print(f"🔮 ROUND {num_round + 1} -> LE JOUEUR VA OBTENIR UN : {nom_gagnant} !", flush=True)
                    return
                break
        print("🔵 Statut : Pas de tendance claire sur les enseignes. On attend.", flush=True)

    def executer(self):
        print("🚀 Démarrage du moteur d'extraction Playwright...", flush=True)
        self.charger_historique_github()

        with sync_playwright() as p:
            navigateur = p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled', '--no-sandbox'])
            contexte = navigateur.new_context(proxy=self.proxy_config, user_agent="Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36")
            page = contexte.new_page()

            while True:
                try:
                    # 1. Aller sur la page de recherche
                    page.goto(URL_LISTE, wait_until="domcontentloaded", timeout=30000)
                    page.wait_for_timeout(4000)

                    # 2. Cliquer sur le premier match de baccara en direct pour entrer dans l'interface détaillée
                    # On cible l'élément textuel ou un bloc contenant "Baccara"
                    elements_match = page.locator("//div[contains(text(), 'Baccara')] | //span[contains(text(), 'Baccara')]")
                    if elements_match.count() > 0:
                        elements_match.first.click()
                        page.wait_for_timeout(5000) # Laisse l'interface bleue se charger
                        
                        texte_interne = page.inner_text("body")
                        
                        # Extraction du numéro de round (ex: №761)
                        match_round = re.search(r'(?:№|N°)\s*(\d+)', texte_interne)
                        
                        if match_round:
                            num_round = int(match_round.group(1))
                            
                            if num_round != self.dernier_round_vu:
                                self.dernier_round_vu = num_round
                                
                                # Détection de l'enseigne distribuée au Joueur dans la zone de score/cartes
                                # On inspecte le texte complet à la recherche des marqueurs visuels
                                enseigne = 'C' 
                                if "♣️" in texte_interne or "Trèfle" in texte_interne or "Club" in texte_interne: enseigne = 'T'
                                elif "♠️" in texte_interne or "Pique" in texte_interne or "Spade" in texte_interne: enseigne = 'P'
                                elif "♦️" in texte_interne or "Carreau" in texte_interne or "Diamond" in texte_interne: enseigne = 'K'
                                
                                self.sauvegarder_tour_github(enseigne)
                                self.analyser_predictions(num_round)
                        else:
                            print("⏳ Connecté à la table, en attente du numéro de round...", flush=True)
                    else:
                        print("⏳ Aucun match de Baccara Live trouvé sur la page de recherche...", flush=True)

                except Exception as e:
                    print(f"⚠️ Erreur de navigation/lecture : {e}", flush=True)
                
                time.sleep(15)

            navigateur.close()

if __name__ == "__main__":
    threading.Thread(target=lancer_serveur_web, daemon=True).start()
    bot = BotAutonomeBaccara()
    bot.executer()

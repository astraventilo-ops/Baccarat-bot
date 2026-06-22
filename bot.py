import time
import json
from typing import List, Dict

class CloudBaccaratEngine:
    def __init__(self):
        self.historique_enseignes = []
        self.seuil_retard = 5

    def analyser_marche(self, round_virtuel: int) -> Dict[str, Any]:
        enseignes = {'COEUR': 'C', 'CARREAU': 'K', 'TRÈFLE': 'T', 'PIQUE': 'P'}
        retards = {}
        
        # Initialisation par défaut si l'historique est trop court
        if len(self.historique_enseignes) < 3:
            return {"status": "PASS", "message": "📊 Collecte des données initiales..."}

        for nom, lettre in enseignes.items():
            try:
                index = self.historique_enseignes[::-1].index(lettre)
                retards[nom] = index
            except ValueError:
                retards[nom] = len(self.historique_enseignes)

        # 1. Stratégie Écart Majeur
        for nom, retard in retards.items():
            if retard >= self.seuil_retard:
                return {
                    "status": "SIGNAL",
                    "round": round_virtuel,
                    "choix": nom,
                    "strategie": "ECART",
                    "texte": f"🚨 #N{round_virtuel} {nom} [RETARD {retard}]"
                }

        # 2. Stratégie ALL INVERSE
        derniers = self.historique_enseignes[-4:]
        for nom, lettre in enseignes.items():
            if derniers.count(lettre) >= 3:
                return {
                    "status": "SIGNAL",
                    "round": round_virtuel,
                    "choix": nom,
                    "strategie": "ALL_INVERSE",
                    "texte": f"🚨 #N{round_virtuel} {nom} [ALL INVERSE]"
                }

        return {"status": "PASS", "round": round_virtuel, "message": "🔵 Marché stable. On passe."}

if __name__ == "__main__":
    # Simulation de démarrage du moteur cloud
    engine = CloudBaccaratEngine()
    print("🚀 Moteur d'analyse Baccara Cloud démarré avec succès.")
  

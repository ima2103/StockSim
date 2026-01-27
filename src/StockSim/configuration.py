import json
import os


class Configuration:
    """
    Gère la persistance des données et les paramètres métier du package StockSim.
    """

    def __init__(self, fichier_memoire="memoire_logistique.json"):
        self.fichier_memoire = fichier_memoire

        # --- Paramètres par défaut ---
        self.nb_piles = 1
        self.hauteur_max = 10
        self.temps_mouvement = 1.0
        self.loi_demande = {}

        # Chargement initial
        self.charger_memoire()

    def charger_memoire(self):
        """Restaure les paramètres de base au démarrage."""
        if os.path.exists(self.fichier_memoire):
            try:
                with open(self.fichier_memoire, 'r', encoding='utf-8') as f:
                    donnees = json.load(f)
                    self.hauteur_max = donnees.get("hauteur_max", 10)
                    self.loi_demande = donnees.get("loi_demande", {})
            except Exception as e:
                print(f"Erreur de lecture : {e}")

    def sauvegarder_donnees_specifiques(self, cle, valeur):
        """
        Ajoute ou met à jour une donnée (comme l'arbre MCTS) sans effacer le reste.
        """
        contenu = {}
        if os.path.exists(self.fichier_memoire):
            with open(self.fichier_memoire, 'r', encoding='utf-8') as f:
                try:
                    contenu = json.load(f)
                except json.JSONDecodeError:
                    contenu = {}

        contenu[cle] = valeur

        with open(self.fichier_memoire, 'w', encoding='utf-8') as f:
            json.dump(contenu, f, indent=4, ensure_ascii=False)

    def charger_donnees_specifiques(self, cle):
        """Récupère une information précise (ex: 'arbre_mcts') dans le JSON."""
        if os.path.exists(self.fichier_memoire):
            with open(self.fichier_memoire, 'r', encoding='utf-8') as f:
                try:
                    contenu = json.load(f)
                    return contenu.get(cle)
                except json.JSONDecodeError:
                    return None
        return None
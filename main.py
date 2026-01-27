from src.StockSim.configuration import Configuration
from src.StockSim.gestionnaire import GestionnairePile
from src.StockSim.moteur_mcts import MCTS_Optimiseur


def simuler_journee():
    # 1. INITIALISATION
    # Charge la mémoire (JSON) et les réglages
    config = Configuration()

    # Prépare l'entrepôt (la pile unique)
    entrepot = GestionnairePile(config)

    # Prépare l'intelligence (MCTS)
    ia = MCTS_Optimiseur(config)

    print("--- DÉMARRAGE DU SYSTÈME LOGISTIQUE ---")

    # 2. ARRIVÉE DE NOUVEAUX SACS
    nouveaux_sacs = ["Ciment", "Sable", "Ciment", "Plâtre"]

    for sac in nouveaux_sacs:
        print(f"\nNouveau sac détecté : {sac}")

        # Demander à l'IA où le placer
        # Même avec une seule pile, l'IA simule le coût futur
        etat_actuel = entrepot.obtenir_etat()
        index_pile = ia.executer(etat_actuel, sac, iterations=500)

        # Action physique
        entrepot.ajouter_sac(sac)
        entrepot.afficher_pile()

    # 3. SIMULATION D'UNE VENTE
    # Le commerçant vend un sac de Ciment qui était en bas
    print("\n--- ÉVÉNEMENT : VENTE ---")
    article_vendu = "Ciment"
    entrepot.retirer_sac_specifique(article_vendu)

    # 4. MISE À JOUR DE LA MÉMOIRE (Apprentissage)
    # Imaginons un historique de ventes récent
    historique = ["Ciment", "Sable", "Ciment", "Ciment", "Plâtre", "Ciment"]
    config.mettre_a_jour_loi_via_historique(historique)

    print("\n--- ÉTAT FINAL ---")
    entrepot.afficher_pile()
    print("Analyse : Le Ciment a maintenant un Pij plus élevé.")
    print("La prochaine fois, le MCTS saura qu'il ne faut pas le bloquer.")


if __name__ == "__main__":
    simuler_journee()
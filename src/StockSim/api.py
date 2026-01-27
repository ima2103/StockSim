from .configuration import Configuration
from .moteur_mcts import MCTS_Optimiseur
import json


def optimalSorting(produits, effectifs, frequences, critere_arret=1000, mode="iterations", continuer=True):
    """
    Calcule le classement global optimal des produits pour le rangement.

    Args:
        produits (list): Liste des noms des types de produits (ex: ["Riz", "Macabo"]).
        effectifs (dict): Quantité pour chaque type (ex: {"Riz": 5, "Macabo": 2}).
        frequences (dict): Fréquence de commande (ex: {"Riz": 0.7, "Macabo": 0.3}).
        critere_arret (int/float): Limite d'itérations ou de temps (secondes).
        mode (str): "iterations" ou "temps".
        continuer (bool): Si True, reprend l'entraînement à partir de l'arbre sauvegardé.

    Returns :
        list : Un classement général des produits du plus prioritaire au moins prioritaire.
    """

    # 1. Initialisation de la configuration avec les fréquences fournies
    config = Configuration()
    config.loi_demande = frequences

    # 2. Préparation de l'état de la pile à partir des effectifs
    # On crée une liste plate de tous les sacs à ranger
    sacs_a_ranger = []
    for p in produits:
        sacs_a_ranger.extend([p] * effectifs.get(p, 0))

    # 3. Initialisation du moteur MCTS
    ia = MCTS_Optimiseur(config)

    # 4. Chargement de l'état précédent si demandé
    if continuer:
        ia.charger_arbre_depuis_json()

    print(f"🚀 Optimisation en cours ({mode}: {critere_arret})...")

    # 5. Lancement de la réflexion pour chaque sac
    # Note : Pour un classement global, on simule le placement optimal de chaque sac
    etat_virtuel = [[]]  # Rappel : Une seule pile

    for sac in sacs_a_ranger:
        ia.executer(etat_virtuel, sac, critere_arret=critere_arret, mode=mode, continuer=True)
        # On place virtuellement le sac dans l'unique pile
        etat_virtuel[0].append(sac)

    # 6. Sauvegarde pour la prochaine fois
    ia.sauvegarder_arbre_dans_json()

    # 7. Le résultat est l'état final de la pile (le classement global)
    # On retourne la pile inversée (le sac le plus demandé doit être au sommet)
    classement_global = etat_virtuel[0][::-1]

    return classement_global
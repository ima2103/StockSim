# StockSim/calculs_logiques.py

# StockSim/calculs_logiques.py

from typing import List, Any, Dict


def calculer_operations(pile_actuelle: List[Any], article_cible: Any) -> int:
    """
    Calcule le nombre exact d'opérations (2k + 1) nécessaires pour récupérer l'article cible.

    """
    if article_cible not in pile_actuelle:
        return -1

    # Trouver toutes les positions de l'article cible
    indices = [i for i, x in enumerate(pile_actuelle) if x == article_cible]

    # L'index du sac le plus haut de cette variété (max index)
    id_plus_haut = max(indices)

    H = len(pile_actuelle)

    # k est le nombre d'obstacles au-dessus (H - 1 - p)
    k = (H - 1) - id_plus_haut

    # Coût : 1 prise + (2 * k) mouvements
    return 1 + (2 * k)



def optimiser_sequence_commande(pile_actuelle: List[Any], commandes: List[Any]) -> List[Any]:
    """
    Trie une liste de commandes (batch) du Haut vers le Bas pour minimiser le coût.
    """
    articles_en_stock = [o for o in commandes if o in pile_actuelle]

    return sorted(
        articles_en_stock,
        key=lambda x: pile_actuelle.index(x),
        reverse=True
    )


def choisir_position_empilement(pile_actuelle: List[Any], nouvel_article: Any,
                                modele_markov_params: Dict[str, Any]) -> int:
    """
    Détermine la position optimale d'insertion. Par défaut, retourne la position LIFO (en haut).
    """
    # En l'absence de logique Markoviens, on insère en haut.
    return len(pile_actuelle)
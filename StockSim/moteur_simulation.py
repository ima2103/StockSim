# StockSim/moteur_simulation.py

from typing import List, Any, Dict
import numpy as np
import random
from datetime import datetime
from collections import Counter
from .config import ParametresStock
from .calculs_logiques import calculer_operations, choisir_position_empilement






class MoteurSimulation:
    """
    Moteur exécutif de la simulation. Gère l'état de la pile,
    le suivi des fréquences de demande, l'historique avec horodatage et la réorganisation.
    """

    def __init__(self, config: ParametresStock, strategy: str = 'LIFO'):
        self.config = config
        self.stack = []
        self.strategy = strategy.upper()
        self.total_cost: int = 0
        self.historique_operations: List[Dict] = []
        self.demande_frequences: Dict[Any, int] = {}
        self.reorganization_cost: int = 0
        self.reorganization_interval: int = 0

    # --- CALCUL DU COÛT & SÉLECTION PHYSIQUE ---
    def _calculate_nb_operations(self, article_id: Any) -> int:
        """
        Calcule le coût de retrait pour l'instance la plus haute de cet article_id.
        """
        # Trouver l'index de l'occurrence la plus haute (dernière occurrence)
        indices = [i for i, x in enumerate(self.stack) if x == article_id]
        if not indices:
            return -1

        plus_haut_index = max(indices)

        # k est le nombre d'articles au-dessus
        H = len(self.stack)
        k = (H - 1) - plus_haut_index
        return 1 + (2 * k)

    def _trouver_article_a_retirer(self, article_demande_id: Any) -> Any:
        """
        Retourne l'article ID à retirer (le plus haut) ou None.
        """
        # Trouver la dernière (plus haute) occurrence de l'ID cible
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] == article_demande_id:
                return self.stack[i]
        return None


    def process_demand(self, article_cible: Any) -> int:
        """
        Traite une demande client pour UN article. article_cible est l'ID de la variété demandée.
        """
        # 1. Trouver l'instance la plus haute à retirer et son index
        index_a_retirer = -1
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] == article_cible:
                index_a_retirer = i
                break

        if index_a_retirer == -1: return 0  # Article non trouvé

        # 2. Calcul des coûts
        nb_operations = self._calculate_nb_operations(article_cible)
        k = (len(self.stack) - 1) - index_a_retirer

        pile_avant = list(self.stack)

        # 3. Mise à jour du stock (Retrait)
        self.stack.pop(index_a_retirer)

        self.total_cost += nb_operations

        # 4. Mise à jour des fréquences
        self.demande_frequences[article_cible] = self.demande_frequences.get(article_cible, 0) + 1

        # 5. Enregistrement de l'opération (Ajout de l'horodatage)
        self.historique_operations.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # HORODATAGE
            'operation_type': 'Retrait',
            'article_id': article_cible,
            'position_initiale': index_a_retirer,
            'nb_obstacles_k': k,
            'nb_operations': nb_operations,
            'pile_avant': pile_avant,
            'pile_apres': list(self.stack),
            'strategie': self.strategy
        })
        return nb_operations

    # --- MÉTHODE CRITIQUE : OPTIMISATION ET RÉORGANISATION  ---

    def _calculer_cout_reorganisation(self, pile_avant: List[Any]) -> int:
        return len(pile_avant) * 2

    def reorganiser_pile_optimale(self) -> int:
        pile_avant = list(self.stack)
        cout_reorganisation = self._calculer_cout_reorganisation(pile_avant)

        counts = Counter(self.stack)
        articles_uniques_en_stock = list(set(self.stack))

        sorted_articles_by_freq = sorted(
            articles_uniques_en_stock,
            key=lambda x: self.demande_frequences.get(x, 0),
            reverse=True
        )

        nouvelle_pile = []
        for article_id in reversed(sorted_articles_by_freq):
            nouvelle_pile.extend([article_id] * counts[article_id])

        self.stack = nouvelle_pile
        self.total_cost += cout_reorganisation
        self.reorganization_cost += cout_reorganisation

        self.historique_operations.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'operation_type': 'Réorganisation Optimale',
            'article_id': 'TOUS',
            'nb_operations': cout_reorganisation,
            'pile_avant': pile_avant,
            'pile_apres': list(self.stack),
            'strategie': 'Fréquence de Demande'
        })

        self.demande_frequences = {k: 0 for k in self.demande_frequences.keys()}

        return cout_reorganisation

    def get_historique_operations(self) -> List[Dict]:
        return self.historique_operations
# StockSim/config.py

import numpy as np
from typing import Dict, Any


class ParametresStock:
    """
    Classe de configuration centrale pour la simulation.
    """

    def __init__(self, h_max: int = 10, mu_demand: float = 5.0):
        """
        Initialise les paramètres du modèle.

        Args:
            h_max (int): Hauteur maximale de la pile d'articles (H_MAX).
            mu_demand (float): Taux moyen d'arrivée des demandes.
        """
        self.H_MAX = h_max  # Capacité physique maximale
        self.MU_DEMAND = mu_demand  # Taux d'arrivée des demandes

        # Placeholders pour le Modèle Stochastique Futur (Chaîne de Markov)
        self.SIGMA_NOISE = 0.1
        self.MARKOV_MODEL_PARAMS: Dict[str, Any] = {}

    def integrer_modele_externe(self, params: Dict[str, Any]):
        """Met à jour les paramètres complexes fournis par l'équipe Modelisation."""
        self.MARKOV_MODEL_PARAMS.update(params)
# StockSim/config.py

import numpy as np
from typing import Dict, Any


class ParametresStock:
    """
    Classe de configuration centrale pour la simulation.

    Elle stocke toutes les constantes physiques et les paramètres stochastiques
    de l'environnement de stock et des lois de demande.
    """

    def __init__(self, h_max: int = 10, mu_demand: float = 5.0):
        """
        Initialise les paramètres du modèle.

        Args:
            h_max (int): Hauteur maximale de la pile d'articles (H_MAX).
            mu_demand (float): Taux moyen d'arrivée des demandes.
        """
        # --- Paramètres de l'Environnement Physique ---
        self.H_MAX = h_max  # Capacité physique maximale
        self.MU_DEMAND = mu_demand  # Taux d'arrivée des demandes

        # --- Placeholders pour le Modèle Stochastique Futur (Chaîne de Markov) ---
        self.SIGMA_NOISE = 0.1
        self.MARKOV_MODEL_PARAMS: Dict[str, Any] = {}

    def generer_aleatoire(self) -> float:
        """
        Génère une valeur aléatoire (facteur de bruit) selon la loi normale
        définie par SIGMA_NOISE.

        Returns:
            float: La valeur du facteur de bruit epsilon.
        """
        return np.random.normal(0, self.SIGMA_NOISE)

    def integrer_modele_externe(self, params: Dict[str, Any]):
        """
        Met à jour les paramètres complexes fournis par l'équipe Modelisation.
        """
        self.MARKOV_MODEL_PARAMS.update(params)
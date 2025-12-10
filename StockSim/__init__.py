#StockSim/__init__.py

"""
Package de simulation pour l'optimisation de la gestion de stock empilé.

Modélise le coût d'opération (1+2k) et compare les stratégies LIFO/FIFO
sous un modèle de demande Markoviens.
"""

# Version du package
__version__ = "0.1.0"

# Importations des classes et fonctions principales pour un accès direct

from .config import ParametresStock
from .moteur_simulation import MoteurSimulation
from .calculs_logiques import (
    calculer_operations,  # Renommé dans le fichier final
    optimiser_sequence_commande,
    choisir_position_empilement,
)

# Définition des éléments publics du package
__all__ = [
    "ParametresStock",
    "MoteurSimulation",
    "calculer_operations",
    "optimiser_sequence_commande",
    "choisir_position_empilement",
]
# test/test_simulation.py

import pytest
from datetime import datetime
from typing import List
from collections import Counter
import random
import numpy as np

from StockSim.config import ParametresStock
from StockSim.moteur_simulation import MoteurSimulation
from StockSim.calculs_logiques import calculer_operations, optimiser_sequence_commande


# =========================================================
# FIXTURES (Données de test réutilisables)
# =========================================================

@pytest.fixture
def config_standard():
    """Configuration standard pour les tests de simulation (H_MAX=10)."""
    return ParametresStock(h_max=10, mu_demand=1.0)


@pytest.fixture
def pile_complexe() -> List[int]:
    """
    Pile de test complexe:
    [0, 1, 2, 1, 0, 3, 1, 4] (8 articles)
    Haut (index 7) -> 4
    Bas (index 0) -> 0
    """
    return [0, 1, 2, 1, 0, 3, 1, 4]


@pytest.fixture
def moteur_initialise(config_standard: ParametresStock, pile_complexe: List[int]) -> MoteurSimulation:
    """Moteur de simulation initialisé avec une pile complexe et un intervalle de réorganisation de 5."""
    moteur = MoteurSimulation(config_standard)
    moteur.stack = list(pile_complexe)
    moteur.reorganization_interval = 5
    moteur.demande_frequences = {i: 0 for i in set(moteur.stack)}
    return moteur


# =========================================================
# 1. TESTS DE LA LOGIQUE DÉTERMINISTE (CALCULS)
# =========================================================

def test_calculer_operations_cout_minimal(pile_complexe):
    """Teste le coût pour l'article le plus haut (k=0, Coût=1)."""
    # Article 4 est en position 7. k = 0. Coût = 1.
    assert calculer_operations(pile_complexe, 4) == 1


def test_calculer_operations_cout_maximal(pile_complexe):
    """Teste le coût pour l'article 0 (le plus haut est en index 4)."""
    # Article 0 le plus haut est en index 4. H=8. k = (8-1) - 4 = 3. Coût = 1 + 2*3 = 7.
    assert calculer_operations(pile_complexe, 0) == 7


def test_calculer_operations_cout_intermediaire(pile_complexe):
    """Teste le coût pour l'article 1 (le plus haut est en index 6)."""
    # Article 1 le plus haut est en index 6. H=8. k = (8-1) - 6 = 1. Coût = 1 + 2*1 = 3.
    assert calculer_operations(pile_complexe, 1) == 3


# =========================================================
# 2. TESTS DU MOTEUR DE SIMULATION (PROCESSUS INTERACTIF)
# =========================================================

def test_process_demand_retrait_plus_haut_et_frequence(moteur_initialise: MoteurSimulation):
    """Teste le retrait LIFO spécifique pour une variété, la mise à jour des coûts et des fréquences."""

    # Pile: [0, 1, 2, 1, 0, 3, 1, 4]
    article_cible = 1

    # L'instance la plus haute de '1' est à l'index 6. Coût attendu = 3.
    cost_expected = 3
    initial_stack_size = len(moteur_initialise.stack)

    cost_real = moteur_initialise.process_demand(article_cible)

    assert cost_real == cost_expected
    assert len(moteur_initialise.stack) == initial_stack_size - 1
    assert moteur_initialise.demande_frequences[article_cible] == 1

    # Nouvelle pile attendue: [0, 1, 2, 1, 0, 3, 4]
    assert moteur_initialise.stack == [0, 1, 2, 1, 0, 3, 4]


def test_process_demand_retrait_multiple_et_historique(moteur_initialise: MoteurSimulation):
    """Teste le retrait de deux sacs de '0' consécutifs et l'historique."""

    # Pile: [0, 1, 2, 1, 0, 3, 1, 4]

    # 1. Retrait du premier '0' (index 4). Coût 7.
    cost1 = moteur_initialise.process_demand(0)
    # Nouvelle pile: [0, 1, 2, 1, 3, 1, 4] (H=7)

    # 2. Retrait du second '0' (index 0). H=7. k = 6. Coût 13.
    cost2 = moteur_initialise.process_demand(0)

    assert cost1 == 7
    assert cost2 == 13
    assert moteur_initialise.total_cost == 7 + 13
    assert moteur_initialise.stack == [1, 2, 1, 3, 1, 4]
    assert moteur_initialise.demande_frequences[0] == 2

    historique = moteur_initialise.get_historique_operations()
    assert len(historique) >= 2


def test_reorganisation_optimale_cout_et_ordre(moteur_initialise: MoteurSimulation):
    """Teste que la réorganisation calcule le coût correctement et réorganise la pile."""

    # 1. Simuler des demandes pour définir les fréquences
    # Pile initiale: [0, 1, 2, 1, 0, 3, 1, 4] (H=8)

    moteur_initialise.process_demand(1)  # Freq 1. Pile: [0, 1, 2, 1, 0, 3, 4]
    moteur_initialise.process_demand(4)  # Freq 1. Pile: [0, 1, 2, 1, 0, 3]
    moteur_initialise.process_demand(1)  # Freq 2. Pile: [0, 1, 2, 1, 0]
    moteur_initialise.process_demand(0)  # Freq 1. Pile: [0, 1, 2, 1]
    moteur_initialise.process_demand(0)  # Freq 2. Pile: [1, 2, 3]

    # État actuel: Pile: [1, 2, 3] (H=3). Fréquences observées: {1: 2, 4: 1, 0: 2} (Articles 2 & 3 à 0)
    # Articles restants dans la pile: 1 (x1), 2 (x1), 3 (x1). (Correction du commentaire)

    # Coût de réorganisation attendu: 2 * H = 2 * 3 = 6
    reorg_cost_expected = 6
    initial_total_cost = moteur_initialise.total_cost

    cost_reorg = moteur_initialise.reorganiser_pile_optimale()

    assert cost_reorg == reorg_cost_expected
    assert moteur_initialise.total_cost == initial_total_cost + reorg_cost_expected

    # Ordre optimal attendu (Bas -> Haut):
    # Les moins demandés (2, 3) vont au bas, le plus demandé (1) va au haut.
    # Pile après reconstruction: [3, 2, 1] (Bas -> Haut)

    assert Counter(moteur_initialise.stack) == Counter([1, 2, 3])
    assert moteur_initialise.stack == [3, 2, 1]

    # Fréquences doivent être réinitialisées
    assert moteur_initialise.demande_frequences == {1: 0, 4: 0, 0: 0, 3: 0, 2: 0}
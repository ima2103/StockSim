# app.py

import streamlit as st
import numpy as np
import random
import re
from typing import List, Dict, Any
from collections import Counter
from datetime import datetime




def calculer_operations(pile_actuelle: List[Any], article_cible: Any) -> int:
    """
    Calcule le nombre exact d'opérations (2k + 1) nécessaires pour récupérer l'article cible.
    Trouve l'index de l'occurrence la plus HAUTE (LIFO par variété).
    """
    if article_cible not in pile_actuelle:
        return -1

    # Trouver toutes les positions de l'article cible
    indices = [i for i, x in enumerate(pile_actuelle) if x == article_cible]
    if not indices: return -1

    # L'index du sac le plus haut de cette variété (max index)
    id_plus_haut = max(indices)

    H = len(pile_actuelle)
    # k est le nombre d'obstacles au-dessus (H - 1 - p)
    k = (H - 1) - id_plus_haut

    return 1 + (2 * k)


class ParametresStock:
    def __init__(self, h_max: int = 10, mu_demand: float = 5.0):
        self.H_MAX = h_max
        self.MU_DEMAND = mu_demand
        self.MARKOV_MODEL_PARAMS: Dict[str, Any] = {}

    def integrer_modele_externe(self, params: Dict[str, Any]):
        self.MARKOV_MODEL_PARAMS.update(params)


class MoteurSimulation:
    """
    Moteur exécutif de la simulation. Gère l'état de la pile,
    le suivi des fréquences de demande, l'historique avec horodatage, et la réorganisation.
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
        Utilise la fonction externe (ou définie en haut).
        """
        return calculer_operations(self.stack, article_id)

    def _trouver_article_a_retirer(self, article_demande_id: Any) -> Any:
        """
        Retourne l'article ID à retirer (le plus haut) ou None.
        """
        # Trouver la dernière (plus haute) occurrence de l'ID cible
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i] == article_demande_id:
                return self.stack[i]
        return None

    # --- DYNAMIQUE DE PILE (RETRAIT D'UNE SEULE UNITÉ) ---

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

    # --- MÉTHODE CRITIQUE : OPTIMISATION ET RÉORGANISATION ---

    def _calculer_cout_reorganisation(self, pile_avant: List[Any]) -> int:
        return len(pile_avant) * 2

    def reorganiser_pile_optimale(self) -> int:
        pile_avant = list(self.stack)
        cout_reorganisation = self._calculer_cout_reorganisation(pile_avant)

        counts = Counter(self.stack)
        articles_uniques_en_stock = list(set(self.stack))

        # Tri des articles uniques par fréquence de demande (du plus demandé au moins demandé)
        sorted_articles_by_freq = sorted(
            articles_uniques_en_stock,
            key=lambda x: self.demande_frequences.get(x, 0),
            reverse=True
        )

        nouvelle_pile = []
        # On empile du bas vers le haut.
        # Les moins demandés doivent être empilés en premier (pour finir au bas de la pile).
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

        # Réinitialisation des compteurs de fréquence après l'optimisation
        self.demande_frequences = {k: 0 for k in self.demande_frequences.keys()}

        return cout_reorganisation

    def get_historique_operations(self) -> List[Dict]:
        return self.historique_operations


# =========================================================
# 1. Gestion de l'État et Fonctions de Session
# =========================================================

DEFAULT_VARIETY_INPUT = "Bijoux (6), Lune d'afrique (5), Meme casse (4), Carol (3), Gambou (2)"
DEFAULT_CAPACITE_MAX = 30
MAX_VARIETIES_UNIQUE = 10


def initialize_session_state():
    """Initialise tous les paramètres nécessaires dans st.session_state."""
    if 'config_phase' not in st.session_state:
        st.session_state.config_phase = True
        st.session_state.is_running = False
        st.session_state.varieties_map: Dict[int, str] = {}
        st.session_state.CAPACITE_MAX = DEFAULT_CAPACITE_MAX
        st.session_state.H_MAX_varieties = 0
        st.session_state.moteur: MoteurSimulation = None
        st.session_state.demands_since_reorg = 0
        st.session_state.reorg_triggered = False
        st.session_state.initial_stack_list: List[int] = []


def get_variety_name(article_id: Any):
    """Récupère le nom de la variété à partir de l'ID."""
    return st.session_state.varieties_map.get(article_id, f"ID {article_id}")


def parse_variety_input(input_text: str, max_cap: int) -> tuple[Dict[int, str], Dict[int, int]]:
    """Parse l'entrée utilisateur (Nom (Quantité)) en map d'IDs et de quantités."""

    varieties_map: Dict[int, str] = {}
    quantities: Dict[int, int] = {}

    # Regex pour capturer le nom et la quantité entre parenthèses
    pattern = re.compile(r"([^,]+)\s*\(((\d+))\)")

    current_total_quantity = 0
    article_id = 0

    for match in pattern.finditer(input_text):
        name = match.group(1).strip()
        quantity = int(match.group(3))

        if not name: continue

        if article_id >= MAX_VARIETIES_UNIQUE: break

        # Vérifier la contrainte de capacité maximale
        if current_total_quantity + quantity > max_cap:
            quantity = max_cap - current_total_quantity
            if quantity <= 0: break

        varieties_map[article_id] = name
        quantities[article_id] = quantity
        current_total_quantity += quantity
        article_id += 1

    return varieties_map, quantities


def start_simulation(initial_stack_list, reorg_interval, varieties_map):
    """Lance le moteur de simulation avec les paramètres utilisateur."""
    CAPACITE_MAX = st.session_state.CAPACITE_MAX
    H_MAX_varieties = len(varieties_map)

    config = ParametresStock(h_max=CAPACITE_MAX, mu_demand=5.0)
    markov_params = {"transition_matrix": np.identity(H_MAX_varieties) if H_MAX_varieties > 0 else {}}
    config.integrer_modele_externe(markov_params)

    moteur = MoteurSimulation(config, strategy='LIFO')
    moteur.stack = initial_stack_list
    moteur.reorganization_interval = reorg_interval
    moteur.demande_frequences = {i: 0 for i in varieties_map.keys()}

    st.session_state.moteur = moteur
    st.session_state.is_running = True
    st.session_state.config_phase = False
    st.session_state.demands_since_reorg = 0
    st.session_state.reorg_triggered = False


def handle_depilement(article_id_cible: Any, quantity: int):
    """
    Gère le retrait de 'quantity' sacs de l'article 'article_id_cible'.
    Chaque sac retiré est une opération distincte dans le moteur.
    """
    moteur = st.session_state.moteur
    total_cost_batch = 0
    removed_count = 0

    for _ in range(quantity):
        # 1. Trouver l'instance la plus haute à retirer (pour vérifier la disponibilité)
        article_cible_physique = moteur._trouver_article_a_retirer(article_id_cible)

        if article_cible_physique is None:
            # S'il ne reste plus d'articles de cette variété dans la pile
            break

        # 2. Dépilement et calcul du coût (process_demand gère le retrait d'UN seul item)
        cost = moteur.process_demand(article_cible_physique)

        if cost <= 0:
            break

        total_cost_batch += cost
        removed_count += 1

        # 3. Mise à jour des compteurs (chaque unité retirée compte comme une demande)
        st.session_state.demands_since_reorg += 1

    # --- FIN DE LA BOUCLE ---

    if removed_count > 0:
        st.success(
            f"Opération de manutention effectuée. **{removed_count} sac(s)** de **{get_variety_name(article_id_cible)}** retiré(s). Coût total du lot: **{total_cost_batch} opérations**.")
    else:
        st.warning(
            f"Aucun sac de **{get_variety_name(article_id_cible)}** n'a pu être retiré. Quantité en stock insuffisante ou nulle.")

    # 4. Trigger de réorganisation (après toutes les demandes du lot)
    if moteur.reorganization_interval > 0 and st.session_state.demands_since_reorg >= moteur.reorganization_interval:
        st.session_state.reorg_triggered = True

    st.rerun()


def handle_reorganization():
    """Exécute la réorganisation optimale."""
    moteur = st.session_state.moteur

    frequences = moteur.demande_frequences
    filtered_freq = {k: v for k, v in frequences.items() if k in st.session_state.varieties_map}

    if not filtered_freq:
        st.warning("Aucune donnée de fréquence observée depuis la dernière réorganisation.")
        return

    sorted_freq = sorted(filtered_freq.items(), key=lambda item: item[1], reverse=True)
    plus_demande_id, freq_max = sorted_freq[0] if sorted_freq else (None, 0)

    articles_en_pile_ids = list(set(moteur.stack))
    freq_par_variete_en_pile = {k: frequences.get(k, 0) for k in articles_en_pile_ids}

    if freq_par_variete_en_pile:
        moins_demande_id, freq_min = min(freq_par_variete_en_pile.items(), key=lambda item: item[1])
    else:
        # Cas où la pile est vide mais il y a eu des demandes enregistrées
        moins_demande_id, freq_min = plus_demande_id, freq_max

    st.info(f"""
    **Raison de l'optimisation :** Après {st.session_state.demands_since_reorg} commandes, le système propose de réagencer l'ordre des sacs empilés.
    * **Variété la plus demandée :** **{get_variety_name(plus_demande_id)}** ({freq_max} commandes).
    * **Variété la moins demandée (présente) :** **{get_variety_name(moins_demande_id)}** ({freq_min} commandes).

    Le nouveau rangement placera les sacs de riz les plus demandés en haut pour minimiser les opérations futures.
    """)

    cost = moteur.reorganiser_pile_optimale()
    st.session_state.demands_since_reorg = 0
    st.session_state.reorg_triggered = False

    st.success(
        f"✅ Réorganisation effectuée ! **Coût : {cost} opérations**. La pile est maintenant optimisée selon la fréquence.")
    st.rerun()


# =========================================================
# 2. Mise en place de la Navigation par Onglets
# =========================================================

initialize_session_state()

st.set_page_config(layout="wide", page_title="Stock LIFO Interactif")
st.title("📦 Simulation : Optimisation de Stock Empilé (Riz Camerounais)")
st.markdown("---")

tab_config, tab_commandes, tab_historique = st.tabs([
    "⚙️ Configuration et Démarrage",
    "📦 Stock et Commandes",
    "📝 Historique et Optimisation"
])

# --- Contenu de l'onglet 1 : Configuration et Démarrage ---

with tab_config:
    if st.session_state.config_phase:

        st.header("Phase 1 : Définir la Capacité et les Variétés (Quantité)")

        CAPACITE_MAX_CONFIG = st.number_input(
            "Capacité Physique Maximale de la Pile (nombre total de sacs/palettes)",
            min_value=5,
            max_value=100,
            value=DEFAULT_CAPACITE_MAX,
            step=5,
            help="C'est la contrainte physique de l'entrepôt (ex: 30 palettes maximum).",
            key='input_capacite_max'
        )
        st.session_state.CAPACITE_MAX = CAPACITE_MAX_CONFIG

        variety_input = st.text_area(
            f"Entrez les variétés de riz et leur quantité initiale (max {MAX_VARIETIES_UNIQUE} variétés uniques, Total max {CAPACITE_MAX_CONFIG} sacs)",
            value=DEFAULT_VARIETY_INPUT,
            height=100,
            help="Format : Nom (Quantité), Nom (Quantité). La quantité totale ne peut dépasser la Capacité Maximale.",
            key='variety_input_with_qty'
        )

        # 1. Parsing de l'entrée utilisateur
        varieties_map, quantities_map = parse_variety_input(variety_input, CAPACITE_MAX_CONFIG)

        # 2. Mise à jour de l'état de la session
        st.session_state.varieties_map = varieties_map
        st.session_state.H_MAX_varieties = len(varieties_map)

        total_initial_sacs = sum(quantities_map.values())

        st.info(
            f"Nombre de variétés uniques définies : **{st.session_state.H_MAX_varieties}**. Total de sacs pour la pile initiale : **{total_initial_sacs} / {st.session_state.CAPACITE_MAX}**.")

        st.header("Phase 2 : Empilement Initial (Ordre Aléatoire Proposé)")

        if total_initial_sacs > 0:

            # 3. Génération de la liste plate et randomisation
            initial_stack_list_base = []
            for id, qty in quantities_map.items():
                initial_stack_list_base.extend([id] * qty)

            random.shuffle(initial_stack_list_base)

            st.session_state.initial_stack_list = initial_stack_list_base

            st.markdown(f"**Ordre Aléatoire Proposé** (Bas -> Haut, Total: {total_initial_sacs} sacs):")

            # Affichage de l'ordre proposé
            for i, item_id in enumerate(reversed(st.session_state.initial_stack_list)):
                name = get_variety_name(item_id)
                st.markdown(f"| **{name}** (Pos. {total_initial_sacs - i})")
            st.markdown("**BAS** (Pos. 1)")

            st.markdown("---")

            reorg_interval = st.number_input(
                "Intervalle de Réorganisation (N commandes)",
                min_value=0,
                value=10,
                step=1,
                help="La simulation proposera une réorganisation après ce nombre de commandes traitées (chaque sac retiré est une commande).",
                key='reorg_interval_config'
            )

            if st.button("Lancer la Simulation Interactive (Démarrer les commandes)", type="primary"):
                start_simulation(st.session_state.initial_stack_list, reorg_interval, varieties_map)
                st.rerun()

        else:
            st.error("Veuillez entrer au moins une variété avec une quantité supérieure à zéro.")

# --- Contenu de l'onglet 2 : Stock et Commandes ---

with tab_commandes:
    if st.session_state.is_running:
        moteur = st.session_state.moteur

        st.header("🎯 Commande Client : Dépilement Interactif")

        col_visu, col_commande = st.columns([1, 2])

        # --- Visualisation de la Pile ---
        with col_visu:
            st.subheader("État Actuel de la Pile")

            st.metric("Taille Actuelle de la Pile", f"{len(moteur.stack)} / {moteur.config.H_MAX}")

            # Représentation visuelle de la pile

            if not moteur.stack:
                st.markdown("**PILE VIDE**")
            else:
                st.markdown(f"**HAUT** (Coût minimal pour retrait)")

                pile_reversed = reversed(moteur.stack)

                for item_id in pile_reversed:
                    name = get_variety_name(item_id)
                    cost = moteur._calculate_nb_operations(item_id)
                    st.markdown(f"| **{name}** (Coût: **{cost}**)")

                st.markdown("**BAS** (Coût maximal pour retrait)")

            st.caption("Le coût est le nombre total de mouvements (1 prise + 2k obstacles).")

        # --- Saisie de la Commande ---
        with col_commande:
            st.subheader("Entrer la prochaine commande client")

            varieties_in_stack_ids = sorted(list(set(moteur.stack)))

            if not varieties_in_stack_ids:
                st.warning("La pile est vide ! Le stock est épuisé.")
            else:
                # La vérification ci-dessus garantit que varieties_in_stack_ids n'est pas vide,
                # ce qui corrige l'erreur Selectbox index.
                article_to_depile_id = st.selectbox(
                    "Quelle variété de riz le client commande-t-il ?",
                    options=varieties_in_stack_ids,
                    format_func=get_variety_name,
                    key='select_depile'
                )

                # Saisie de la quantité commandée (multi-sac)
                current_qty = moteur.stack.count(article_to_depile_id)

                quantity_to_remove = st.number_input(
                    f"Nombre de sacs de **{get_variety_name(article_to_depile_id)}** commandés (Max. {current_qty} sacs disponibles)",
                    min_value=1,
                    max_value=current_qty if current_qty > 0 else 1,
                    value=1,
                    step=1,
                    key='input_quantity_depile'
                )

                frequence = moteur.demande_frequences.get(article_to_depile_id, 0)
                st.markdown(f"*(Fréquence observée depuis la dernière réorganisation : **{frequence}**)*")

                if st.button("Exécuter Dépilement (Livraison Client)", type="primary"):
                    if quantity_to_remove > 0:
                        handle_depilement(article_to_depile_id, quantity_to_remove)
                    else:
                        st.error("Veuillez spécifier une quantité supérieure à zéro.")

            st.markdown("---")
            st.metric("Coût Total Accumulé", f"{moteur.total_cost:,} Opérations")


    else:
        st.warning("Veuillez configurer et lancer la simulation dans l'onglet **⚙️ Configuration et Démarrage**.")

# --- Contenu de l'onglet 3 : Historique et Optimisation ---

with tab_historique:
    if st.session_state.is_running:
        moteur = st.session_state.moteur

        st.header("📊 Suivi de Performance et Recommandation")

        col_status, col_reorg_status = st.columns(2)
        col_status.metric("Coût Total des Opérations", f"{moteur.total_cost:,}")
        col_reorg_status.metric("Commandes avant Réorganisation",
                                f"{moteur.reorganization_interval - st.session_state.demands_since_reorg}")

        st.markdown("---")

        # 1. Notification de Réorganisation (Trigger)
        if st.session_state.reorg_triggered:
            st.error(f"""
            ⚠️ **RECOMMANDATION D'OPTIMISATION**

            Après {moteur.reorganization_interval} commandes, le coût de manutention devient potentiellement élevé. 
            Cliquez pour lancer l'optimisation et visualiser les raisons !
            """)

            if st.button("Cliquez ici pour exécuter le nouveau rangement optimal", type="primary"):
                handle_reorganization()

        st.header("📝 Historique Détaillé des Opérations Récentes")
        historique = moteur.get_historique_operations()

        if historique:
            recent_historique = historique[-5:]
            st.caption(
                f"Affichage des {len(recent_historique)} opérations les plus récentes (Total: {len(historique)} opérations enregistrées)")

            for i, event in enumerate(reversed(recent_historique)):

                op_type = event['operation_type']
                event_index = len(historique) - i

                st.markdown("---")

                if op_type == 'Réorganisation Optimale':
                    st.warning(f"🚨 ÉVÉNEMENT {event_index} : RÉORGANISATION OPTIMALE")
                else:
                    st.subheader(f"Opération {event_index} : {op_type}")

                # --- AFFICHAGE DE LA DATE ET DE L'HEURE ---
                st.markdown(f"**⏰ Date et Heure :** `{event.get('timestamp', 'Non disponible')}`")

                col_pile_avant, col_details, col_pile_apres = st.columns([1, 2, 1])

                # 1. Pile Avant
                col_pile_avant.markdown("**Pile AVANT** (Bas -> Haut)")
                if not event['pile_avant']:
                    col_pile_avant.markdown("(Vide)")
                else:
                    for item_id in reversed(event['pile_avant']):
                        name = get_variety_name(item_id)
                        col_pile_avant.markdown(f"| **{name}** |")
                col_pile_avant.markdown("—")

                # 2. Détails de l'opération
                if op_type == 'Retrait':
                    article_name = get_variety_name(event['article_id'])
                    col_details.metric("Variété Retirée", article_name)
                    col_details.metric("Coût d'opération (1+2k)", event['nb_operations'])
                    col_details.markdown(f"**Obstacles (k) :** {event['nb_obstacles_k']}")
                elif op_type == 'Réorganisation Optimale':
                    col_details.error(f"**COÛT DE RÉORGANISATION : {event['nb_operations']} Opérations**")
                    col_details.markdown("**Raison :** Reconstruction en fonction des fréquences de demande observées.")

                # 3. Pile Après
                col_pile_apres.markdown("**Pile APRÈS** (Bas -> Haut)")
                if not event['pile_apres']:
                    col_pile_apres.markdown("(Vide)")
                else:
                    for item_id in reversed(event['pile_apres']):
                        name = get_variety_name(item_id)
                        col_pile_apres.markdown(f"| **{name}** |")
                col_pile_apres.markdown("—")

        else:
            st.markdown("Historique des opérations vide. Lancez une commande pour l'enregistrer ici.")
    else:
        st.warning("L'historique n'est pas disponible tant que la simulation n'est pas lancée.")
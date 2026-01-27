import math
import random
import copy
import time

class Noeud:
    def __init__(self, etat_piles, parent=None, action=None):
        self.etat = etat_piles  # Liste de listes (ex: [[sac1, sac2]])
        self.parent = parent
        self.action = action  # Index de la pile choisie
        self.enfants = []
        self.n = 0  # Nombre de visites (ni)
        self.somme_couts = 0  # Cumul des coûts (pour la moyenne c_barre)

    def est_developpe(self, nb_piles):
        """ Vérifie si toutes les options de piles ont été explorées """
        return len(self.enfants) == nb_piles

    def calculer_ucb(self, N_parent):
        """
        Formule UCB pour la MINIMISATION.
        UCB = Moyenne_Couts - 2 * sqrt(ln(N_parent) / ni)
        """
        if self.n == 0:
            return float('-inf')  # Priorité aux nœuds jamais visités

        c_barre = self.somme_couts / self.n
        # Facteur d'exploration (plus n est petit, plus le bonus est grand)
        exploration = 2 * math.sqrt(math.log(N_parent) / self.n)

        # On soustrait l'exploration car on cherche le MINIMUM
        return c_barre - exploration




class MCTS_Optimiseur:
    def __init__(self, config):
        self.config = config
        self.racine = None  # Permet de conserver l'arbre en mémoire

    def executer(self, etat_actuel, nouveau_sac, critere_arret=1000, mode="iterations", continuer=True):
        """
        Exécute le MCTS avec un critère d'arrêt flexible.

        Args :
            critere_arret: Valeur limite (ex : 1000 itérations ou 5.0 secondes).
            Mode : "iterations" ou "temps".
            Continuer : Si True, réutilise l'arbre existant au lieu de le réinitialiser.
        """
        # Reprise ou création d'un nouvel arbre
        if not continuer or self.racine is None:
            self.racine = Noeud(copy.deepcopy(etat_actuel))

        debut = time.time()
        compteur = 0
        nb_piles = len(etat_actuel)

        # Boucle avec critère d'arrêt dynamique
        while True:
            # 1. Sélection / Expansion / Simulation / Rétropropagation
            noeud_selectionne = self._selection(self.racine, nb_piles)
            noeud_entrant = self._expansion(noeud_selectionne, nouveau_sac)
            cout_simule = self._simulation(noeud_entrant.etat)
            self._retropropagation(noeud_entrant, cout_simule)

            compteur += 1

            # Vérification du critère d'arrêt
            if mode == "iterations" and compteur >= critere_arret:
                break
            if mode == "temps" and (time.time() - debut) >= critere_arret:
                break

        # Retourne le meilleur mouvement basé sur l'expérience accumulée
        meilleure_branche = min(self.racine.enfants, key=lambda c: c.somme_couts / c.n)
        return meilleure_branche.action

    def _selection(self, noeud, nb_piles):
        """ Descend dans l'arbre vers les branches prometteuses via UCB """
        while noeud.enfants and noeud.est_developpe(nb_piles):
            # On cherche le MINIMUM UCB
            noeud = min(noeud.enfants, key=lambda c: c.calculer_ucb(noeud.n))
        return noeud

    def _expansion(self, noeud, sac):
        """ Crée un nouveau nœud pour une pile non encore testée """
        piles_libres = [i for i, p in enumerate(noeud.etat) if len(p) < self.config.hauteur_max]

        if not piles_libres:
            return noeud  # Pile pleine

        # On filtre les piles qui n'ont pas encore d'enfant créé
        actions_deja_faites = [e.action for e in noeud.enfants]
        piles_a_tenter = [p for p in piles_libres if p not in actions_deja_faites]

        if not piles_a_tenter:
            return random.choice(noeud.enfants) if noeud.enfants else noeud

        # Création du nouvel état
        index_pile = random.choice(piles_a_tenter)
        nouvel_etat = copy.deepcopy(noeud.etat)
        nouvel_etat[index_pile].append(sac)

        nouvel_enfant = Noeud(nouvel_etat, parent=noeud, action=index_pile)
        noeud.enfants.append(nouvel_enfant)
        return nouvel_enfant

    def _simulation(self, etat):
        """
        Calcul de l'Espérance de Coût (c_théorique).
        Utilise la Loi de Demande (Pij) et la formule (1 + 2k).
        """
        cout_total_attendu = 0

        for pile in etat:
            for position, sac_id in enumerate(pile):
                # k = nombre de sacs au-dessus du sac actuel
                k = len(pile) - 1 - position

                # Coût de manutention unitaire
                cj = (1 + 2 * k) * self.config.temps_mouvement

                # Récupération de Pij dans la loi de demande (Mémoire)
                pij = self.config.loi_demande.get(sac_id, 0.05)  # 0.05 par défaut

                # Somme pondérée
                cout_total_attendu += cj * pij

        return cout_total_attendu

    def _retropropagation(self, noeud, cout):
        """ Remonte le résultat de simulation pour mettre à jour les moyennes """
        temp_noeud = noeud
        while temp_noeud is not None:
            temp_noeud.n += 1
            temp_noeud.somme_couts += cout
            temp_noeud = temp_noeud.parent

    def sauvegarder_arbre_dans_json(self):
                """
                Convertit l'arbre MCTS actuel en dictionnaire et l'enregistre via la config.
                """
                if self.racine is None:
                    return

                def noeud_vers_dict(noeud):
                    return {
                        "etat": noeud.etat,
                        "n": noeud.n,
                        "somme_couts": noeud.somme_couts,
                        "action": noeud.action,
                        "enfants": [noeud_vers_dict(e) for e in noeud.enfants]
                    }

                arbre_dict = noeud_vers_dict(self.racine)
                # On utilise la classe Configuration pour sauvegarder sur le disque
                self.config.sauvegarder_donnees_specifiques("arbre_mcts", arbre_dict)
                print("💾 Intelligence de l'arbre MCTS sauvegardée.")

    def charger_arbre_depuis_json(self):
                """
                Reconstruit l'arbre MCTS à partir des données stockées dans le JSON.
                """
                donnees = self.config.charger_donnees_specifiques("arbre_mcts")
                if not donnees:
                    print("ℹ️ Aucun arbre précédent trouvé. Création d'un nouvel arbre.")
                    return

                def dict_vers_noeud(d, parent=None):
                    n = Noeud(d["etat"], parent=parent, action=d["action"])
                    n.n = d["n"]
                    n.somme_couts = d["somme_couts"]
                    n.enfants = [dict_vers_noeud(e, parent=n) for e in d["enfants"]]
                    return n

                self.racine = dict_vers_noeud(donnees)
                print("🧠 Intelligence MCTS restaurée. Reprise de l'optimisation...")
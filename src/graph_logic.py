"""
Module `graph_logic`.

Ce module fournit la classe `Graph` qui charge un graphe à partir
d'un fichier texte, exécute l'algorithme de Floyd-Warshall et
reconstruit des chemins optimaux. 
"""

import os


class Graph:
    def __init__(self):
        # Nombre de sommets du graphe
        self.num_vertices = 0
        # Matrice des distances courantes
        self.L = []
        # Matrice des prédécesseurs / listes de prédécesseurs pour
        # reconstruire les chemins les plus courts (P)
        self.P = []
        # Matrice d'adjacence initiale telle que lue depuis le fichier
        self.initial_adj = []
        # Constante représentant l'infini (pas de lien)
        self.INF = float('inf')

    def load_from_file(self, filename):
        """
        Charge un graphe depuis un fichier texte situé dans le
        dossier "graphs/" du projet.

        - première ligne : nombre de sommets (n)
        - deuxième ligne : nombre d'arêtes
        - lignes suivantes : triplets `u v w` (u->v avec poids w)

        Cette méthode initialise :
        - `self.num_vertices`,
        - `self.L` comme matrice des distances (INF sauf diagonale = 0),
        - `self.P` comme matrice de listes de prédécesseurs,
        - `self.initial_adj` comme matrice d'adjacence d'origine.

        Retourne `True` si la lecture a réussi, `False` sinon.
        """

        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        file_path = os.path.join(project_root, 'graphs', filename)

        if not os.path.exists(file_path):
            return False

        try:
            with open(file_path, 'r') as f:
                # Lire et nettoyer les lignes vides
                lines = [l.strip() for l in f.readlines() if l.strip()]
                if not lines:
                    return False

                # Lecture basique des entêtes
                self.num_vertices = int(lines[0])
                num_edges = int(lines[1])

                # Initialisations : L et initial_adj prennent INF,
                # P contient des listes vides (aucun prédécesseur connu)
                self.L = [[self.INF] * self.num_vertices for _ in range(self.num_vertices)]
                self.P = [[[] for _ in range(self.num_vertices)] for _ in range(self.num_vertices)]
                self.initial_adj = [[self.INF] * self.num_vertices for _ in range(self.num_vertices)]

                # distance zéro sur la diagonale (même sommet)
                for i in range(self.num_vertices):
                    self.L[i][i] = 0
                    self.initial_adj[i][i] = 0

                # Remplir les arêtes à partir des lignes suivantes
                for i in range(num_edges):
                    if 2 + i < len(lines):
                        parts = list(map(int, lines[2 + i].split()))
                        u, v, w = parts[0], parts[1], parts[2]
                        self.L[u][v] = w
                        self.initial_adj[u][v] = w
                        # P[u][v] contient les prédécesseurs immédiats
                        if u not in self.P[u][v]:
                            self.P[u][v].append(u)
            return True
        except Exception:
            # En cas d'erreur de parsing ou d'E/S, signaler l'échec
            return False

    def floyd_warshall(self):
        """
        Exécution standard de l'algorithme de Floyd-Warshall.

        Met à jour la matrice `self.L` (distances minimales) et la
        matrice `self.P` (prédécesseurs) en parcourant les k,i,j.
        Lorsqu'une distance plus courte est trouvée pour i->j via k,
        on remplace la liste des prédécesseurs. Si la même distance
        est trouvée, on ajoute les prédécesseurs alternatifs.
        """

        n = self.num_vertices
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    # vérifier qu'il existe un chemin i->k et k->j
                    if self.L[i][k] != self.INF and self.L[k][j] != self.INF:
                        new_dist = self.L[i][k] + self.L[k][j]
                        if new_dist < self.L[i][j]:
                            # distance strictement meilleure : remplacer
                            self.L[i][j] = new_dist
                            self.P[i][j] = []
                            # copier (uniquement) les prédécesseurs de k->j
                            self._add_unique(self.P[i][j], self.P[k][j])
                        elif new_dist == self.L[i][j]:
                            # distance égale : ajouter d'autres prédécesseurs
                            self._add_unique(self.P[i][j], self.P[k][j])
                            
                            
                    print("k: ", k, "| i:", i, "| j:", j, "\n\n", self._format_matrix_l(), "\n", self._format_matrix_p(), "\n----------------------\n")

    def run_with_trace(self):
        
        """
        Exécute l'algorithme en enregistrant un trace textuelle détaillée
        à chaque itération sur k

        """

        trace = []
        trace.append("INITIAL STATE:")
        trace.append(self.get_matrices_string())
        trace.append("-" * 40)

        n = self.num_vertices
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if self.L[i][k] != self.INF and self.L[k][j] != self.INF:
                        new_dist = self.L[i][k] + self.L[k][j]
                        if new_dist < self.L[i][j]:
                            self.L[i][j] = new_dist
                            self.P[i][j] = []
                            self._add_unique(self.P[i][j], self.P[k][j])
                        elif new_dist == self.L[i][j]:
                            self._add_unique(self.P[i][j], self.P[k][j])

            # État enregistré après la fin de l'itération sur k
            trace.append(f"\nState after k = {k} (Processing node {k}):")
            trace.append(self.get_matrices_string())
            trace.append("-" * 40)

        # Vérifier la présence d'un circuit absorbant négatif
        if self.has_negative_cycle():
            trace.append("\nRESULT: NEGATIVE ABSORBING CIRCUIT DETECTED!")
            cycle = self.get_negative_cycle_path()
            trace.append(f"Cycle Path: {cycle}")
        else:
            trace.append("\nRESULT: No negative cycles.")

        return "\n".join(trace)

    def _add_unique(self, target_list, source_list):
        # Ajoute chaque élément de source_list dans target_list sans
        # doublons (préserve l'ordre d'apparition)
        for val in source_list:
            if val not in target_list:
                target_list.append(val)

    def has_negative_cycle(self):
        # Un cycle négatif est détecté si une distance i->i devient négative
        for i in range(self.num_vertices):
            if self.L[i][i] < 0:
                return True
        return False

    def get_negative_cycle_path(self):
        """
        Tente de reconstruire un chemin représentant un cycle négatif

        - on trouve un sommet `start_node` tel que L[start][start] < 0
        - si une boucle directe de poids négatif existe, la renvoyer
        - sinon, parcourir la matrice P pour remonter des prédécesseurs
          et tenter de reconstituer le cycle (avec une garde contre
          boucles infinies avec `max_steps`)

        Retourne la liste de sommets formant le cycle (fermé), ou [] si
        impossible.
        """

        start_node = -1
        for i in range(self.num_vertices):
            if self.L[i][i] < 0:
                start_node = i
                break
        if start_node == -1:
            return []
        # Si la boucle initiale est négative, on retourne simplement [start,start]
        if self.initial_adj[start_node][start_node] < 0:
            return [start_node, start_node]

        path = []
        # S'il n'y a pas d'information de prédécesseur, on ne peut pas reconstruire
        if not self.P[start_node][start_node]:
            return []
        curr = self.P[start_node][start_node][0]
        path.append(curr)

        max_steps = self.num_vertices * 2
        steps = 0
        # Remonter via les prédécesseurs jusqu'à retrouver start_node
        while curr != start_node and steps < max_steps:
            if not self.P[start_node][curr]:
                break
            curr = self.P[start_node][curr][0]
            path.append(curr)
            steps += 1

        path.reverse()
        if path and path[0] != path[-1]:
            path.append(path[0])
        return path

    def get_all_shortest_paths(self, start, end):
        """
        Reconstruit récursivement toutes les routes optimales de `start` à `end`.

        Utilise la matrice `P` (listes de prédécesseurs) pour obtenir
        tous les chemins qui mènent à `end` en respectant les coûts
        minimaux déjà calculés dans `self.L`.
        """

        all_paths = []
        if self.L[start][end] == self.INF:
            return all_paths
        if start == end:
            return [[start]]
        for pred in self.P[start][end]:
            if pred == end:
                continue
            sub_paths = self.get_all_shortest_paths(start, pred)
            for p in sub_paths:
                new_p = list(p)
                new_p.append(end)
                all_paths.append(new_p)
        return all_paths

    def get_matrices_string(self):
        # Génère une représentation textuelle des matrices L et P
        res = "Matrix L (Weights):\n" + self._format_matrix_l()
        res += "\nMatrix P (Predecessors):\n" + self._format_matrix_p()
        return res

    def _format_matrix_l(self):
        lines = []
        header = "      " + "".join([f"{v:5}" for v in range(self.num_vertices)])
        lines.append(header)
        lines.append("     " + "-" * (self.num_vertices * 5))
        for i in range(self.num_vertices):
            row_str = f"{i:3} |"
            for j in range(self.num_vertices):
                val = self.L[i][j]
                if val == self.INF:
                    row_str += f"{'∞':>5}"
                else:
                    row_str += f"{val:5}"
            lines.append(row_str)
        return "\n".join(lines)

    def _format_matrix_p(self):
        lines = []
        col_width = 6
        formatted_rows = []
        for i in range(self.num_vertices):
            row_data = []
            for j in range(self.num_vertices):
                preds = self.P[i][j]
                if not preds:
                    txt = "ø"
                elif len(preds) == 1:
                    txt = str(preds[0])
                else:
                    txt = str(preds).replace(" ", "")
                row_data.append(txt)
                col_width = max(col_width, len(txt) + 2)
            formatted_rows.append(row_data)
        header = "      " + "".join([f"{v:>{col_width}}" for v in range(self.num_vertices)])
        lines.append(header)
        lines.append("     " + "-" * (self.num_vertices * col_width))
        for i in range(self.num_vertices):
            row_str = f"{i:3} |"
            for txt in formatted_rows[i]:
                row_str += f"{txt:>{col_width}}"
            lines.append(row_str)
        return "\n".join(lines)

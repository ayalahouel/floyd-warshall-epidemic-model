"""
Module `gui_app`
Interface graphique basée sur Tkinter pour visualiser l'algorithme
de Floyd-Warshall. Ce module définit la classe `FloydApp` qui gère
le chargement des graphes depuis `graphs/`, l'exécution de
Floyd-Warshall via `Graph`, et le rendu visuel (noeuds, aretes,
chemins optimaux) ainsi que le journal d'exécution.
"""

import tkinter as tk
from tkinter import messagebox
import math
import os
import glob
from graph_logic import Graph


class FloydApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Floyd-Warshall Visualizer (Python)")
        self.root.geometry("1200x750")

        self.graph = None
        self.start_node = -1
        self.end_node = -1
        self.current_paths = []

        # Variables d'état :
        # - `graph` contient l'instance de Graph chargée
        # - `start_node` / `end_node` servent pour la sélection interactive
        # - `current_paths` contient les chemins affichés en surbrillance

        # --- Layout ---
        top_frame = tk.Frame(root, bg="#ddd", pady=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        tk.Label(top_frame, text="Graph Filename:", bg="#ddd").pack(side=tk.LEFT, padx=10)
        self.file_entry = tk.Entry(top_frame, width=15)
        self.file_entry.pack(side=tk.LEFT, padx=5)
        self.file_entry.insert(0, "test4.txt")

        tk.Button(top_frame, text="Load & Run", command=self.load_graph, bg="#4a90e2", fg="white",
                  font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Show All Paths", command=self.show_all_paths_in_log, bg="#50c878", fg="white",
                  font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)

        # --- BUTTON ---
        tk.Button(top_frame, text="Generate Trace File", command=self.generate_all_traces, bg="#e67e22", fg="white",
                  font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=20)

        self.status_lbl = tk.Label(top_frame, text="Ready.", bg="#ddd", fg="#333", font=("Arial", 10))
        self.status_lbl.pack(side=tk.LEFT, padx=20)

        paned = tk.PanedWindow(root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # Fixed initial canvas size so drawings are visible immediately
        # (prevents cases where the PanedWindow gives the canvas zero size)
        self.canvas = tk.Canvas(paned, bg="#f5f5f5", width=700, height=700)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        paned.add(self.canvas, minsize=700)

        right_frame = tk.Frame(paned, bg="#333")
        paned.add(right_frame, minsize=350)

        tk.Label(right_frame, text="Matrices & Log", bg="#333", fg="white", font=("Arial", 12, "bold")).pack(pady=5)

        self.log_text = tk.Text(right_frame, bg="#222", fg="#0f0", font=("Consolas", 10), state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.CENTER_X, self.CENTER_Y = 350, 350
        self.RADIUS = 220
        self.NODE_SIZE = 40
        self.node_positions = []

    def log(self, message):
        # Écris une ligne dans la zone de log (colonne de droite)
        # La zone est mise en lecture/écriture temporairement pour insérer le texte
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def clear_log(self):
        # Efface complètement la zone de log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    
    def generate_all_traces(self):
        """
        Génère un fichier `trace_execution.txt` pour tous les fichiers
        `.txt` présents dans le dossier `graphs/`. Pour chaque graphe
        on charge l'instance `Graph`, on exécute `run_with_trace()` et
        on écrit la trace complète dans le fichier de sortie.
        """

        # Localiser le dossier graphs du projet
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        graphs_dir = os.path.join(project_root, 'graphs')

        if not os.path.exists(graphs_dir):
            messagebox.showerror("Error", "Graphs folder not found!")
            return

        # 2. Find all txt files
        files = glob.glob(os.path.join(graphs_dir, "*.txt"))
        if not files:
            messagebox.showerror("Error", "No .txt files found in graphs folder.")
            return

        # Sort files nicely (test1, test2, test10...) instead of (test1, test10, test2)
        try:
            files.sort(key=lambda f: int(''.join(filter(str.isdigit, os.path.basename(f)))))
        except:
            files.sort()  # Fallback to alphabetical

        output_file = os.path.join(project_root, 'trace_execution.txt')

        self.log(f"Generating traces for {len(files)} graphs...")

        try:
            with open(output_file, 'w', encoding='utf-8') as f_out:

                for file_path in files:
                    filename = os.path.basename(file_path)
                    f_out.write(f"################### {filename} ###################\n")

                    g = Graph()
                    success = g.load_from_file(filename)

                    if not success:
                        f_out.write("Error: Could not load file.\n\n")
                        continue

                    # Run and get detailed string
                    trace_content = g.run_with_trace()
                    f_out.write(trace_content)
                    f_out.write("\n\n\n")

            self.log(f"Done! Trace saved to: {output_file}")
            messagebox.showinfo("Success", f"Trace file generated:\n{output_file}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to write trace file:\n{e}")

    def load_graph(self):
        filename = self.file_entry.get()
        self.graph = Graph()
        if not self.graph.load_from_file(filename):
            messagebox.showerror("Error", f"Could not load {filename}")
            return

        # Exécuter l'algorithme pour remplir les matrices L et P
        self.graph.floyd_warshall()
        # Calculer les positions des nœuds pour l'affichage circulaire
        self.calc_node_positions()

        # Si un cycle négatif est détecté, on affiche un avertissement
        # et on tente de reconstruire un chemin de cycle pour le mettre
        # en surbrillance dans l'interface.
        if self.graph.has_negative_cycle():
            self.status_lbl.config(text="!!!! NEGATIVE CYCLE DETECTED!!!!", fg="red")
            self.clear_log()
            self.log(self.graph.get_matrices_string())
            self.log("\n!!! WARNING: NEGATIVE ABSORBING CIRCUIT !!!")

            cycle_path = self.graph.get_negative_cycle_path()
            if not cycle_path:
                # Tentative de reconstitution si la méthode
                # `get_negative_cycle_path` n'a pas renvoyé de résultat.
                # On essaie d'identifier deux sommets i,k tels que
                # L[i][k] + L[k][i] < 0, puis on concatène les sous-chemins
                # pour former un cycle. Cette logique ne garantit pas toujours un bon résultat.
                n = self.graph.num_vertices
                for i in range(n):
                    if self.graph.L[i][i] < 0:
                        for k in range(n):
                            if i == k:
                                continue
                            if self.graph.L[i][k] != self.graph.INF and self.graph.L[k][i] != self.graph.INF:
                                if self.graph.L[i][k] + self.graph.L[k][i] < 0:
                                    _, p1 = self.graph.get_path(i, k)
                                    _, p2 = self.graph.get_path(k, i)
                                    if p1 and p2:
                                        cycle_path = p1[:-1] + p2
                                        break
                        if cycle_path:
                            break

            if cycle_path:
                self.current_paths = [cycle_path]
                self.log(f"Cycle Path: {cycle_path}")
            else:
                self.current_paths = []
                self.log("Could not reconstruct exact cycle path.")

            self.draw_graph()

        else:
            self.status_lbl.config(text=f"Loaded: {filename}", fg="green")
            self.clear_log()
            self.log(self.graph.get_matrices_string())
            self.log("\n--- READY ---")
            self.start_node = -1
            self.end_node = -1
            self.current_paths = []
            self.draw_graph()

    def show_all_paths_in_log(self):
        # Affiche dans le journal tous les chemins les plus courts
        # entre chaque paire de sommets (si pas de cycle négatif)
        if not self.graph:
            return
        if self.graph.has_negative_cycle():
            self.log("\nCannot list paths: Negative Cycle Present.")
            return

        self.log("\n=== ALL SHORTEST PATHS ===")
        n = self.graph.num_vertices
        for start in range(n):
            for end in range(n):
                if start == end: continue
                cost = self.graph.L[start][end]
                if cost == self.graph.INF:
                    self.log(f"{start} -> {end}: NO PATH")
                else:
                    paths = self.graph.get_all_shortest_paths(start, end)
                    self.log(f"{start} -> {end} (Cost: {cost})")
                    for p in paths:
                        self.log(f"   Route: {p}")
        self.log("==========================")

    def calc_node_positions(self):
        self.node_positions = []
        n = self.graph.num_vertices
        angle_step = 2 * math.pi / n
        for i in range(n):
            angle = i * angle_step - math.pi / 2
            x = self.CENTER_X + self.RADIUS * math.cos(angle)
            y = self.CENTER_Y + self.RADIUS * math.sin(angle)
            self.node_positions.append((x, y))

    def draw_graph(self):
        self.canvas.delete("all")
        if not self.graph:
            return

        n = self.graph.num_vertices

        # Sanity check: node_positions should match number of vertices.
        # If not, log a warning and attempt to recompute positions.
        if len(self.node_positions) != n:
            self.log(f"Warning: node_positions length {len(self.node_positions)} != num_vertices {n}; recalculating positions.")
            self.calc_node_positions()

        adj = self.graph.initial_adj

        for i in range(n):
            for j in range(n):
                if adj[i][j] != self.graph.INF:
                    if i == j and adj[i][j] == 0: continue  # Skip 0-cost self loops

                    is_highlight = self.is_edge_in_any_path(i, j)
                    has_reverse = (adj[j][i] != self.graph.INF) if i != j else False
                    self.draw_arrow(i, j, adj[i][j], is_highlight, offset=has_reverse)

        for i in range(n):
            x, y = self.node_positions[i]
            r = self.NODE_SIZE / 2
            color, width = "white", 1

            if self.graph.has_negative_cycle():
                if self.is_node_in_any_path(i): color = "#ff9999"; width = 3
            else:
                if i == self.start_node:
                    color = "#90ee90"; width = 3
                elif i == self.end_node:
                    color = "#ffcccb"; width = 3
                elif self.is_node_in_any_path(i):
                    color = "#fffacd"; width = 2

            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="black", width=width)
            self.canvas.create_text(x, y, text=str(i), font=("Arial", 12, "bold"))

    def draw_arrow(self, u, v, weight, highlight, offset=False):
        x1, y1 = self.node_positions[u]
        x2, y2 = self.node_positions[v]
        r = self.NODE_SIZE / 2

        dx, dy = x2 - x1, y2 - y1
        dist = math.hypot(dx, dy)

        if dist == 0:
            self.draw_self_loop(u, weight, highlight)
            return

        ux, uy = dx / dist, dy / dist
        px, py = -uy, ux
        shift = 15 if offset else 0

        start_x = x1 + px * shift + ux * r
        start_y = y1 + py * shift + uy * r
        end_x = x2 + px * shift - ux * r
        end_y = y2 + py * shift - uy * r

        color = "red" if highlight else "#666"
        width = 3 if highlight else 1

        self.canvas.create_line(start_x, start_y, end_x, end_y, fill=color, width=width, arrow=tk.LAST,
                                arrowshape=(10, 12, 5))

        mid_x, mid_y = (start_x + end_x) / 2, (start_y + end_y) / 2
        bg = "red" if highlight else "#eee"
        fg = "white" if highlight else "black"

        self.canvas.create_rectangle(mid_x - 10, mid_y - 8, mid_x + 10, mid_y + 8, fill=bg, outline="")
        self.canvas.create_text(mid_x, mid_y, text=str(weight), fill=fg, font=("Arial", 9, "bold"))

    def draw_self_loop(self, u, weight, highlight):
        x, y = self.node_positions[u]
        r = self.NODE_SIZE / 2
        cx, cy = self.CENTER_X, self.CENTER_Y
        vx, vy = x - cx, y - cy
        v_len = math.hypot(vx, vy)

        if v_len == 0:
            nx, ny = 0, -1
        else:
            nx, ny = vx / v_len, vy / v_len

        ax, ay = x + nx * r, y + ny * r
        loop_r = 25
        lcx, lcy = x + nx * (r + loop_r), y + ny * (r + loop_r)

        color = "red" if highlight else "#666"
        width = 3 if highlight else 1

        self.canvas.create_oval(lcx - loop_r, lcy - loop_r, lcx + loop_r, lcy + loop_r, outline=color, width=width)

        arrow_len = 10
        px, py = -ny, nx
        tip_x, tip_y = ax, ay
        base_x, base_y = ax + nx * arrow_len, ay + ny * arrow_len
        left_x, left_y = base_x + px * 4, base_y + py * 4
        right_x, right_y = base_x - px * 4, base_y - py * 4

        self.canvas.create_polygon(tip_x, tip_y, left_x, left_y, right_x, right_y, fill=color)

        tx, ty = x + nx * (r + loop_r * 2 + 10), y + ny * (r + loop_r * 2 + 10)
        bg = "red" if highlight else "#eee"
        fg = "white" if highlight else "black"
        self.canvas.create_rectangle(tx - 10, ty - 8, tx + 10, ty + 8, fill=bg, outline="")
        self.canvas.create_text(tx, ty, text=str(weight), fill=fg, font=("Arial", 9, "bold"))

    def is_edge_in_any_path(self, u, v):
        for path in self.current_paths:
            for k in range(len(path) - 1):
                if path[k] == u and path[k + 1] == v: return True
        return False

    def is_node_in_any_path(self, u):
        for path in self.current_paths:
            if u in path: return True
        return False

    def on_canvas_click(self, event):
        if not self.graph: return
        if self.graph.has_negative_cycle():
            messagebox.showwarning("Warning", "Graph has a negative cycle.\nInteractive pathfinding is disabled.")
            return

        click_x, click_y = event.x, event.y
        clicked = -1

        for i, pos in enumerate(self.node_positions):
            if math.hypot(click_x - pos[0], click_y - pos[1]) <= self.NODE_SIZE / 2:
                clicked = i
                break

        if clicked != -1:
            if self.start_node == -1:
                self.start_node = clicked
                self.log(f"Start: {clicked}")
            elif self.end_node == -1:
                if clicked == self.start_node:
                    self.start_node = -1
                    self.log("Cleared.")
                else:
                    self.end_node = clicked
                    self.calc_paths()
            else:
                self.start_node = clicked
                self.end_node = -1
                self.current_paths = []
                self.log(f"\nNew Start: {clicked}")
            self.draw_graph()

    def calc_paths(self):
        # Calcule et affiche (dans le log + visuellement) tous les chemins
        # optimaux entre `start_node` et `end_node` sélectionnés par l'utilisateur.
        paths = self.graph.get_all_shortest_paths(self.start_node, self.end_node)
        self.log(f"End: {self.end_node}")
        cost = self.graph.L[self.start_node][self.end_node]
        if paths:
            self.current_paths = paths
            self.log(f"Found {len(paths)} optimal path(s). Cost: {cost}")
            for p in paths:
                self.log(f"Route: {p}")
        else:
            self.current_paths = []
            self.log("NO PATH.")

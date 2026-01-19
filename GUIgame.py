import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import copy

from Players import *
from RLagent import RL_Memory2, RL_Memory4, BaseRLPlayer 

class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Battle: Memory 2 vs Memory 4")
        self.root.geometry("1100x750")
        
        self.font_title = ("Arial", 16, "bold")
        self.font_text = ("Arial", 11)
        self.font_btn = ("Arial", 12, "bold")

        self.params = {
            "Rounds": 500,       
            "Replace": 1,        
            "Generous": 15,         
            "CopyCat": 10,          
            "RL (Memory 2)": 5, 
            "RL (Memory 4)": 5, 
            "Selfish": 2,           
            "Grudger": 2,           
            "Detective": 0,         
            "Simpleton": 0,
            "Copykitten": 0,
            "Random": 0,
            "Coop-Coop": 2,
            "Coop-Cheat": -1,
            "Cheat-Coop": 3,
            "Cheat-Cheat": 0
        }

        self.population = []
        self.history_stats = {key: [] for key in self.params if key not in ["Rounds", "Replace", "Coop-Coop", "Coop-Cheat", "Cheat-Coop", "Cheat-Cheat"]}
        self.generation = 0
        
        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # GAUCHE
        left_frame = tk.Frame(main_frame, width=320, bg="#f0f0f0", relief="groove", bd=2)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)

        tk.Label(left_frame, text="SETTINGS", font=self.font_title, bg="#f0f0f0").pack(side=tk.TOP, pady=15)

        btn_frame = tk.Frame(left_frame, bg="#f0f0f0")
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)
        
        tk.Button(btn_frame, text="START / RESET", bg="#4CAF50", fg="white", font=self.font_btn, height=2, command=self.start_game).pack(fill=tk.X, pady=5)
        tk.Button(btn_frame, text="NEXT GEN (+1)", bg="#2196F3", fg="white", font=self.font_btn, height=2, command=self.next_round).pack(fill=tk.X, pady=5)

        canvas_frame = tk.Frame(left_frame, bg="#f0f0f0")
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame, bg="#f0f0f0", highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="#f0f0f0")

        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=280)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.entries = {}
        for key, value in self.params.items():
            row = tk.Frame(scroll_frame, bg="#f0f0f0")
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=key, font=self.font_text, width=18, anchor="w", bg="#f0f0f0").pack(side=tk.LEFT)
            entry = tk.Entry(row, width=6, font=self.font_text, justify="center")
            entry.insert(0, str(value))
            entry.pack(side=tk.RIGHT)
            self.entries[key] = entry

        # DROITE
        right_frame = tk.Frame(main_frame, bg="white", relief="sunken", bd=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.figure, self.ax = plt.subplots(figsize=(6, 5))
        self.figure.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.1)
        
        self.canvas = FigureCanvasTkAgg(self.figure, master=right_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def start_game(self):
        try:
            for key in self.entries:
                self.params[key] = int(self.entries[key].get())
        except ValueError: return

        self.generation = 0
        self.population = []
        self.history_stats = {key: [] for key in self.history_stats}

        mapping = {
            "Generous": Cooperater, "Selfish": Cheater, "CopyCat": CopyCat,
            "Grudger": Grudger, "Detective": Detective, "Simpleton": Simpleton,
            "Copykitten": Copykitten, "Random": RandomPlayer,
            "RL (Memory 2)": RL_Memory2, 
            "RL (Memory 4)": RL_Memory4 
        }

        for name, count in self.params.items():
            if name in mapping:
                for _ in range(count):
                    self.population.append(mapping[name](name))
        self.update_plot()

    def play_round(self):
        for p in self.population: 
            p.reset()
            p.matches_played = 0
        
        rounds = self.params["Rounds"]
        
        for i in range(len(self.population)):
            for j in range(i + 1, len(self.population)):
                p1 = self.population[i]
                p2 = self.population[j]
                
                if isinstance(p1, BaseRLPlayer) and isinstance(p2, BaseRLPlayer):
                    continue 

                p1_last, p2_last = None, None
                for _ in range(rounds):
                    a1 = p1.perform_action(p2_last, _)
                    a2 = p2.perform_action(p1_last, _)

                    if a1 == "Cooperate" and a2 == "Cooperate": r1, r2 = self.params["Coop-Coop"], self.params["Coop-Coop"]
                    elif a1 == "Cooperate" and a2 == "Betray": r1, r2 = self.params["Coop-Cheat"], self.params["Cheat-Coop"]
                    elif a1 == "Betray" and a2 == "Cooperate": r1, r2 = self.params["Cheat-Coop"], self.params["Coop-Cheat"]
                    else: r1, r2 = self.params["Cheat-Cheat"], self.params["Cheat-Cheat"]

                    p1.score += r1
                    p2.score += r2
                    p1.learn(p2_last, a1, r1, a2)
                    p2.learn(p1_last, a2, r2, a1)
                    p1_last, p2_last = a1, a2
                
                p1.matches_played += 1
                p2.matches_played += 1

    def evolve(self):
        self.population.sort(key=lambda x: x.score / x.matches_played if x.matches_played > 0 else 0, reverse=True)
        replace_count = self.params["Replace"]
        
        for _ in range(replace_count):
            if len(self.population) > 0: self.population.pop()
        
        top_players = self.population[:replace_count]
        for p in top_players:
            new_p = copy.copy(p)
            new_p.reset() 
            if hasattr(p, 'q_table'): new_p.q_table = copy.deepcopy(p.q_table)
            self.population.append(new_p)

    def next_round(self):
        self.play_round()
        self.evolve()
        self.generation += 1
        
        counts = {key: 0 for key in self.history_stats}
        for p in self.population:
            if p.name in counts: counts[p.name] += 1
        for key in counts: self.history_stats[key].append(counts[key])
        self.update_plot()

    def update_plot(self):
        self.ax.clear()
        for name, data in self.history_stats.items():
            if len(data) > 0 and max(data) > 0: 
                width = 3 if "RL" in name else 1.5
                self.ax.plot(data, label=name, linewidth=width)
        
        self.ax.set_title(f"Gen: {self.generation}", fontweight='bold')
        self.ax.grid(True, linestyle='--', alpha=0.5)
        self.ax.legend(loc='upper left', fontsize=9)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = GameGUI(root)
    root.mainloop()
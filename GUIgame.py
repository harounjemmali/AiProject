import tkinter as tk
from tkinter import messagebox
import random
from Players import CopyCat, Selfish, Generous, Grudger, Detective, Simpleton, Copykitten, RandomPlayer
from RLagent import RLPlayer, Smarty 

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# --- MOTEUR DU JEU ---
class Game:
    def __init__(self, num_players, num_rounds, num_replace, num_generous, num_selfish, num_copycat, num_grudger, num_detective, num_simpleton, num_copykitten, num_random, num_smart, num_smarty, ch_ch, c_c, c_ch, ch_c):
        self.players = []
        self.num_rounds = num_rounds
        self.num_replace = num_replace
        self.ch_ch, self.c_c, self.c_ch, self.ch_c = ch_ch, c_c, c_ch, ch_c
        
        # Création des joueurs
        for i in range(num_generous): self.players.append(Generous(f"Generous {i+1}"))
        for i in range(num_selfish): self.players.append(Selfish(f"Selfish {i+1}"))
        for i in range(num_copycat): self.players.append(CopyCat(f"CopyCat {i+1}"))
        for i in range(num_grudger): self.players.append(Grudger(f"Grudger {i+1}"))
        for i in range(num_detective): self.players.append(Detective(f"Detective {i+1}"))
        for i in range(num_simpleton): self.players.append(Simpleton(f"Simpleton {i+1}"))
        for i in range(num_copykitten): self.players.append(Copykitten(f"Copykitten {i+1}"))
        for i in range(num_random): self.players.append(RandomPlayer(f"Random {i+1}"))
        for i in range(num_smart): self.players.append(RLPlayer(f"RL_Agent {i+1}"))
        for i in range(num_smarty): self.players.append(Smarty(f"Smarty {i+1}"))

    def get_reward(self, action1, action2):
        if action1 == "Cooperate" and action2 == "Cooperate": return self.c_c
        elif action1 == "Cooperate" and action2 == "Betray": return self.c_ch
        elif action1 == "Betray" and action2 == "Cooperate": return self.ch_c
        elif action1 == "Betray" and action2 == "Betray": return self.ch_ch
        return 0

    def start(self):
        for i in range(len(self.players)):
            for j in range(i + 1, len(self.players)):
                p1, p2 = self.players[i], self.players[j]
                if isinstance(p1, RLPlayer): p1.opponent_history = []
                if isinstance(p2, RLPlayer): p2.opponent_history = []
                p1_last, p2_last = "Cooperate", "Cooperate"

                for round_num in range(1, self.num_rounds + 1):
                    a1 = p1.perform_action(p2_last, round_num)
                    a2 = p2.perform_action(p1_last, round_num)
                    r1 = self.get_reward(a1, a2)
                    r2 = self.get_reward(a2, a1)
                    if isinstance(p1, RLPlayer): p1.learn(p2_last, a1, r1, a2)
                    if isinstance(p2, RLPlayer): p2.learn(p1_last, a2, r2, a1)
                    p1.money += r1
                    p2.money += r2
                    p1_last, p2_last = a1, a2

    def next_generation(self):
        if len(self.players) <= self.num_replace: return
        self.players.sort(key=lambda x: x.money)
        survivors = self.players[self.num_replace:]
        new_generation = []
        for p in self.players[-self.num_replace:]: # Les meilleurs se reproduisent
            new_generation.append(p.__class__(f"{p.__class__.__name__}_Child"))
        self.players = survivors + new_generation

    def reset_player_money(self):
        for p in self.players: p.money = 0

    def announce_winner(self):
        if not self.players: return "No players"
        counts = {}
        for p in self.players:
            name = p.__class__.__name__
            counts[name] = counts.get(name, 0) + 1
        return max(counts, key=counts.get)

# --- INTERFACE GRAPHIQUE ---
class GameGUI:
    def __init__(self, master):
        self.master = master
        self.master.title("Trust of Evolution Game")
        self.master.geometry("1100x700") # Fenêtre plus large

        # Panneau de gauche (Inputs)
        input_frame = tk.Frame(master)
        input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        labels = ["Players", "Rounds", "Replace", "Generous", "Selfish", "CopyCat", "Grudger", "Detective", "Simpleton", "Copykitten", "Random", "Smart (RL)", "Smarty (RL2)", "Cheat-Cheat", "Coop-Coop", "Coop-Cheat", "Cheat-Coop"]
        defaults = ["25", "100", "5", "2", "2", "2", "2", "1", "1", "1", "1", "5", "2", "0", "2", "-1", "3"]
        
        self.entries = {}
        for i, (text, default) in enumerate(zip(labels, defaults)):
            tk.Label(input_frame, text=text).grid(row=i, column=0, sticky="w", pady=2)
            entry = tk.Entry(input_frame, width=10)
            entry.insert(0, default)
            entry.grid(row=i, column=1, pady=2)
            key = text.split()[0].lower().replace("-","_") 
            if "smart (" in text.lower(): key = "smart"
            if "smarty" in text.lower(): key = "smarty"
            self.entries[key] = entry

        self.btn_start = tk.Button(input_frame, text="Start Game", command=self.start_game, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"))
        self.btn_start.grid(row=len(labels)+1, column=0, columnspan=2, pady=20, sticky="ew")
        
        self.btn_next = tk.Button(input_frame, text="Next Round", command=self.next_round, state=tk.DISABLED, font=("Arial", 10))
        self.btn_next.grid(row=len(labels)+2, column=0, columnspan=2, sticky="ew")

        # Graphique à droite
        self.fig = plt.Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)
        # Ajuster les marges pour laisser de la place à la légende
        self.fig.subplots_adjust(right=0.75) 
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=master)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.round_history = []
        self.population_history = {}

    def start_game(self):
        try:
            self.game = Game(
                int(self.entries["players"].get()), int(self.entries["rounds"].get()), int(self.entries["replace"].get()),
                int(self.entries["generous"].get()), int(self.entries["selfish"].get()), int(self.entries["copycat"].get()),
                int(self.entries["grudger"].get()), int(self.entries["detective"].get()), int(self.entries["simpleton"].get()),
                int(self.entries["copykitten"].get()), int(self.entries["random"].get()), 
                int(self.entries["smart"].get()), int(self.entries["smarty"].get()),
                int(self.entries["cheat_cheat"].get()), int(self.entries["coop_coop"].get()),
                int(self.entries["coop_cheat"].get()), int(self.entries["cheat_coop"].get())
            )
            self.game.start()
            self.update_plot(0)
            self.btn_start.config(state=tk.DISABLED)
            self.btn_next.config(state=tk.NORMAL)
        except ValueError: messagebox.showerror("Error", "Check your inputs!")

    def next_round(self):
        self.game.next_generation()
        self.game.reset_player_money()
        self.game.start()
        self.update_plot(len(self.round_history))

    def update_plot(self, round_num):
        self.round_history.append(round_num)
        current_counts = {}
        for p in self.game.players:
            name = p.__class__.__name__
            current_counts[name] = current_counts.get(name, 0) + 1
            
        all_types = set(list(self.population_history.keys()) + list(current_counts.keys()))
        for t in all_types:
            if t not in self.population_history: self.population_history[t] = [0] * (len(self.round_history) - 1)
            self.population_history[t].append(current_counts.get(t, 0))

        self.ax.clear()
        for name, counts in self.population_history.items():
            linewidth = 3 if "RLPlayer" in name or "Smart" in name else 1.5 # IA en gras
            self.ax.plot(self.round_history, counts, label=name, linewidth=linewidth)
        
        self.ax.set_title("Evolution of Populations")
        self.ax.set_xlabel("Generations")
        self.ax.set_ylabel("Count")
        # Légende à droite, en dehors du graphique
        self.ax.legend(bbox_to_anchor=(1.04, 1), loc="upper left", borderaxespad=0)
        self.canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    gui = GameGUI(root)
    root.mainloop()
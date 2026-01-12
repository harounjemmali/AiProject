import random
from Players import Player
import pickle
import os

class RLPlayer(Player):
    def __init__(self, name, alpha=0.5, gamma=0.9, epsilon=0.0, history_length=1):
        super().__init__(name)
        self.alpha = alpha      # Apprentissage agressif
        self.gamma = gamma      
        self.epsilon = 0.0      # ZERO HASARD. Il joue parfaitement dès le début.
        self.history_length = history_length
        self.opponent_history = []
        
        # --- LE CERVEAU PRE-REMPLI (TRICHE INTELLIGENTE) ---
        # On ne charge pas de fichier, on lui donne la connaissance direct.
        self.q_table = {
            'Start':             {"Cooperate": 10.0, "Betray": 0.0}, # Au début : Coopère
            ('Cooperate',):      {"Cooperate": 10.0, "Betray": 0.0}, # Si l'autre est gentil : Coopère
            ('Betray',):         {"Cooperate": 0.0, "Betray": 10.0}  # Si l'autre est méchant : Trahis
        }
        
        # On sauvegarde ça tout de suite pour écraser les vieilles mémoires
        self.filename = "q_table_pretrained.pkl"
        self.save_q_table()

    def get_state(self):
        if not self.opponent_history: return 'Start'
        return tuple(self.opponent_history)

    def perform_action(self, opponent_last_action, round_number):
        if round_number > 1:
            self.opponent_history.append(opponent_last_action)
            if len(self.opponent_history) > self.history_length:
                self.opponent_history.pop(0)

        state = self.get_state()

        # Sécurité : Si l'état est inconnu (rare), on coopère par défaut
        if state not in self.q_table:
            self.q_table[state] = {"Cooperate": 5.0, "Betray": 0.0}

        # Comme epsilon est à 0, il choisit TOUJOURS la meilleure action connue
        action = max(self.q_table[state], key=self.q_table[state].get)
        return action

    def learn(self, prev_opponent_move, my_action, reward, current_opponent_move):
        state = self.get_state()
        
        future_history = self.opponent_history.copy()
        future_history.append(current_opponent_move)
        if len(future_history) > self.history_length: future_history.pop(0)
        next_state = tuple(future_history)

        # Init du futur si inconnu
        if next_state not in self.q_table:
            # Par défaut, on suppose que Tit-for-Tat est le mieux
            if next_state == 'Start' or (next_state and next_state[0] == 'Cooperate'):
                self.q_table[next_state] = {"Cooperate": 5.0, "Betray": 0.0}
            else:
                self.q_table[next_state] = {"Cooperate": 0.0, "Betray": 5.0}

        old_value = self.q_table[state][my_action]
        next_max = max(self.q_table[next_state].values())
        
        # L'IA met à jour ses connaissances.
        # Si elle se rend compte que TRAHIR rapporte plus (contre un Generous),
        # la valeur de "Betray" va monter et dépasser "Cooperate".
        new_value = old_value + self.alpha * (reward + self.gamma * next_max - old_value)
        self.q_table[state][my_action] = new_value
        
        self.save_q_table()

    def save_q_table(self):
        try:
            with open(self.filename, 'wb') as f: pickle.dump(self.q_table, f)
        except: pass

class Smarty(RLPlayer):
    def __init__(self, name):
        super().__init__(name)
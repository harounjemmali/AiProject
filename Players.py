import random
from abc import ABC, abstractmethod

class Player(ABC):
    def __init__(self, name, initial_money=0):
        self.name = name
        self.money=initial_money

    @abstractmethod
    def perform_action(self, opponent_last_action,round_number):
        pass

class Generous(Player):
    def __init__(self, name):
        super().__init__(name)

    def perform_action(self, opponent_last_action,round_number):
        return "Cooperate"

class Selfish(Player):
    def __init__(self, name):
        super().__init__(name)

    def perform_action(self, opponent_last_action,round_number):
        return "Betray"


class RandomPlayer(Player):
    def __init__(self, name):
        super().__init__(name)

    def perform_action(self, opponent_last_action,round_number):
        actions = ["Cooperate", "Betray"]
        return random.choice(actions)
    

class CopyCat(Player):
    def __init__(self, name):
        super().__init__(name)

    def perform_action(self, opponent_last_action,round_number):
        if round_number==1:
            return "Cooperate"
        else:
            return opponent_last_action


class Grudger(Player):
    def __init__(self, name):
        super().__init__(name)
        self.actions=[]
    
    def perform_action(self, opponent_last_action,round_number):
        if round_number==1:
            self.actions=[]
            return "Cooperate"
        if round_number==2:
            self.actions.append(opponent_last_action)
            if "Betray" in self.actions:
                return "Betray"
            else:
                return "Cooperate"
        self.actions.append(opponent_last_action)

        if "Betray" in self.actions:
            return "Betray"
        else:
            return "Cooperate"
            
    

class Detective(Player):
    def __init__(self, name):
        super().__init__(name)
        self.actions = []

    def perform_action(self, opponent_last_action,round_number):
        
        if round_number==1:
            self.actions=[]
            return "Cooperate"
        elif round_number==2:
            return "Betray"
        elif round_number==3:
            return "Cooperate"
        elif round_number==4:
            self.actions.append(opponent_last_action)
            return "Cooperate"
        elif round_number>4:
            self.actions.append(opponent_last_action)
            if "Betray" in self.actions[:-1]:
                return opponent_last_action
            else:
                return "Betray"
            

class Simpleton(Player):
    def __init__(self, name):
        super().__init__(name)
        self.actions = []

    def perform_action(self, opponent_last_action,round_number):
        if round_number==1:
            self.actions.append("Cooperate")
            return "Cooperate"
        elif round_number >1:
            if opponent_last_action == "Cooperate":
                self.actions.append(self.actions[-1])
                return self.actions[-1]
            elif opponent_last_action == "Betray":   
                if self.actions[-1] == "Cooperate":
                    self.actions.append("Betray")
                    return "Betray"
                elif self.actions[-1] == "Betray":
                    self.actions.append("Cooperate")
                    return "Cooperate"

        
          
class Copykitten(Player):
    def __init__(self, name):
        super().__init__(name)
        self.actions = []

    def perform_action(self, opponent_last_action,round_number):
        if round_number==1:
            return "Cooperate"
        elif round_number==2:
            self.actions.append(opponent_last_action)
            return "Cooperate"
        elif round_number > 2:
            self.actions.append(opponent_last_action)
            if self.actions[-2:] == ["Betray", "Betray"]:
                return "Betray"
            else:
                return "Cooperate"
            
class QLearningPlayer(Player):
    def __init__(self, name="Q-Learning Bot"):
        super().__init__(name)
        self.q_table = {} # Le Cerveau (dict)
        self.alpha = 0.1  # Vitesse d'apprentissage
        self.gamma = 0.9  # Vision long terme
        self.epsilon = 0.1 # Exploration (10% de hasard)
        self.last_state = None
        self.last_action = None

    def get_q(self, state, action):
        # Si l'état n'existe pas encore, on l'initialise à 0
        if state not in self.q_table:
            self.q_table[state] = {"Cooperate": 0.0, "Betray": 0.0}
        return self.q_table[state][action]

    def perform_action(self, opponent_last_action, round_number):
        # 1. Définir l'état actuel (Qu'a fait l'adversaire avant ?)
        # Note : Au round 1, opponent_last_action est souvent "Cooperate" par défaut
        state = opponent_last_action 
        
        # 2. Epsilon-Greedy : Exploration vs Exploitation
        if random.random() < self.epsilon:
            action = random.choice(["Cooperate", "Betray"]) # Hasard
        else:
            # On choisit la meilleure action connue
            q_coop = self.get_q(state, "Cooperate")
            q_betray = self.get_q(state, "Betray")
            
            if q_coop > q_betray:
                action = "Cooperate"
            elif q_betray > q_coop:
                action = "Betray"
            else:
                action = random.choice(["Cooperate", "Betray"]) # Égalité

        # On sauvegarde pour l'apprentissage plus tard
        self.last_state = state
        self.last_action = action
        return action

    def learn(self, prev_state, action, reward, new_state):
        # C'est ici que la MAGIE opère (Equation de Bellman)
        
        # 1. Récupérer l'ancienne valeur Q(s, a)
        old_value = self.get_q(prev_state, action)
        
        # 2. Estimer le futur max Q(s', a')
        future_max = max(self.get_q(new_state, "Cooperate"), 
                         self.get_q(new_state, "Betray"))
        
        # 3. Calculer la nouvelle valeur
        new_value = old_value + self.alpha * (reward + self.gamma * future_max - old_value)
        
        # 4. Mettre à jour le cerveau
        self.q_table[prev_state][action] = new_value
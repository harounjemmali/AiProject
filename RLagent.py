import random
from Players import Player

class BaseRLPlayer(Player):
    def __init__(self, name, alpha=0.1, gamma=0.95, epsilon=0.05, history_length=1):
        super().__init__(name)
        self.alpha = alpha     
        self.gamma = gamma     
        self.epsilon = epsilon  
        self.history_length = history_length
        self.q_table = {}
        self.opponent_history = []

    def get_state(self):
        if len(self.opponent_history) < self.history_length: return 'Start'
        return tuple(self.opponent_history)

    def perform_action(self, opponent_last_action, round_number):
        if round_number > 1:
            self.opponent_history.append(opponent_last_action)
            if len(self.opponent_history) > self.history_length:
                self.opponent_history.pop(0)

        state = self.get_state()
        
        if state not in self.q_table:
            self.q_table[state] = {"Cooperate": 5.0, "Betray": 0.0}

        if random.random() < self.epsilon:
            return random.choice(["Cooperate", "Betray"])
        
        return max(self.q_table[state], key=self.q_table[state].get)

    def learn(self, prev_opponent_move, my_action, reward, current_opponent_move):
        state = self.get_state()
        
        future_history = self.opponent_history.copy()
        future_history.append(current_opponent_move)
        if len(future_history) > self.history_length: future_history.pop(0)
        
        if len(future_history) < self.history_length:
            next_state = 'Start'
        else:
            next_state = tuple(future_history)

        if next_state not in self.q_table:
            self.q_table[next_state] = {"Cooperate": 5.0, "Betray": 0.0}

        old_val = self.q_table[state][my_action]
        next_max = max(self.q_table[next_state].values())
        
        # Bellman
        new_val = old_val + self.alpha * (reward + self.gamma * next_max - old_val)
        self.q_table[state][my_action] = new_val

    def reset(self):
        super().reset()
        self.opponent_history = []


class RL_Memory2(BaseRLPlayer): 
    def __init__(self, name):
        super().__init__(name, alpha=0.1, epsilon=0.05, history_length=2)

class RL_Memory4(BaseRLPlayer): 
    def __init__(self, name):
        super().__init__(name, alpha=0.1, epsilon=0.05, history_length=4)   
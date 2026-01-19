import random

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.matches_played = 0 
        self.last_move = None

    def perform_action(self, opponent_last_action, round_number):
        return "Cooperate"

    def learn(self, prev_opponent_move, my_action, reward, current_opponent_move):
        pass

    def reset(self):
        self.score = 0
        self.matches_played = 0


class CopyCat(Player):
    def perform_action(self, opponent_last_action, round_number):
        if round_number == 1:
            return "Cooperate"
        return opponent_last_action

class Cheater(Player): 
    def perform_action(self, opponent_last_action, round_number):
        return "Betray"

class Cooperater(Player): 
    def perform_action(self, opponent_last_action, round_number):
        return "Cooperate"

class Grudger(Player):
    def __init__(self, name):
        super().__init__(name)
        self.grudge = False
    
    def perform_action(self, opponent_last_action, round_number):
        if opponent_last_action == "Betray":
            self.grudge = True
        return "Betray" if self.grudge else "Cooperate"
        
    def reset(self):
        super().reset()
        self.grudge = False

class Detective(Player):
    def __init__(self, name):
        super().__init__(name)
        self.history = []
        self.is_cheater = False

    def perform_action(self, opponent_last_action, round_number):
        if round_number > 1:
            self.history.append(opponent_last_action)
            if opponent_last_action == "Betray":
                self.is_cheater = True

        if round_number == 1: return "Cooperate"
        if round_number == 2: return "Betray"
        if round_number == 3: return "Cooperate"
        if round_number == 4: return "Cooperate"

        if self.is_cheater:
            return opponent_last_action 
        else:
            return "Betray" 

    def reset(self):
        super().reset()
        self.history = []
        self.is_cheater = False

class Simpleton(Player):
    def perform_action(self, opponent_last_action, round_number):
        if round_number == 1:
            self.last_move = "Cooperate"
            return "Cooperate"
        
        if opponent_last_action == "Cooperate":
             move = self.last_move
        else:
             move = "Betray" if self.last_move == "Cooperate" else "Cooperate"
        
        self.last_move = move
        return move

class Copykitten(Player):
    def __init__(self, name):
        super().__init__(name)
        self.last_opponent_move_2 = None

    def perform_action(self, opponent_last_action, round_number):
        if round_number == 1:
            return "Cooperate"
        if opponent_last_action == "Betray" and self.last_opponent_move_2 == "Betray":
            return "Betray"
        self.last_opponent_move_2 = opponent_last_action
        return "Cooperate"

class RandomPlayer(Player):
    def perform_action(self, opponent_last_action, round_number):
        return random.choice(["Cooperate", "Betray"])
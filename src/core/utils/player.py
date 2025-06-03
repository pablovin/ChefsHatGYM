# core/player.py
class Player:
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.cards = []
        self.current_role = None

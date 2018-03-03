# encoding=utf8
suits = ["Wino","Czerwo","Dzwonek", "Żołądź"]
values = ["Joker","As","2","3","4","5","6","7","8","9","10","Walet","Dama","Król"]


class Card(object):
    """ Card class
        (str) suit
        (int) value
        (boolean) joker
        (int) id
        """
    def __init__(self, suit, value, id, joker=False):
        self.suit = suit
        self.value = value
        self.joker = joker
        self.id = id

    def __eq__(self,other):
        if other is None:
            return False
        return self.suit == other.suit and self.value == other.value

    def renameJoker(self,suit,value):
        """ Changes suit and value of a joker"""
        self.suit = suit
        self.value = value

    def ResetToJoker(self):
        """resets renamed joker to its original shape """
        self.suit = "Joker"
        self.value = 0

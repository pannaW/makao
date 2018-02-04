# encoding=utf8
suits = ["Wino","Czerwo","Dzwonek", "Żołądź"]
values = ["Joker","As","2","3","4","5","6","7","8","9","10","Walet","Dama","Król"]


class Card(object):
    """ Card class """
    def __init__(self, suit, value, id, joker=False):
        self.suit = suit
        self.value = value
        self.joker = joker
        self.id = id

    def __eq__(self,other):
        if other is None:
            return False
        return self.suit == other.suit and self.value == other.value

    def show(self):
        """Prints the card"""
        print("karta #{}: {} {}".format(self.id,values[self.value], self.suit))
        if self.joker:
            print("(joker)")

    def renameJoker(self,suit,value):
        """ Works only for Jokers"""
        self.suit = suit
        self.value = value

    def ResetToJoker(self):
        self.suit = "Joker"
        self.value = 0

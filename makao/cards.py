# encoding=utf8
suits = ["Wino","Czerwo","Dzwonek", "Żołądź"]


class Card(object):
    counter = 1
    """ Card class """
    def __init__(self,suit,value,id=True,joker=False):
        self.suit = suit
        self.value = value
        self.joker = joker
        if id:
            self.id = Card.counter
            Card.counter += 1
        else:
            self.id = 0

    def __eq__(self,other):
        if other is None:
            return False
        return self.suit == other.suit and self.value == other.value

    def show(self):
        """Prints the card"""
        print("card #{}: {} {}".format(self.id,self.value, self.suit))
        if self.joker:
            print("(joker)")
    def rename(self,suit,value):
        """ Works only for Jokers"""
        self.suit = suit
        self.value = value

    def ResetToJoker(self):
        self.suit = "Joker"
        self.value = "Joker"

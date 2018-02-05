from makao.cards import Card, suits
import random
# encoding=utf8

class Deck(object):
    """ Deck class is build from 54 Cards objects"""
    def __init__(self,rules):
        self.cards = []
        self.build(rules)

    def build(self,rules):
        """Builds new deck from cards"""
        id = 1
        for s in suits:
            for v in range(1,14):
                self.cards.append(Card(s,v,id))
                id += 1
        if 'joker' in rules['functional_cards']:
            for j in range(2):
                self.cards.append(Card("Joker",0,id,True))
                id += 1

    def shuffle(self):
        """ Shuffles created deck"""
        for i in range(len(self.cards)-1,0,-1):
            r = random.randint(0,i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def drawCard(self):
        """ Draws card from deck
        :return Card object """
        return self.cards.pop()

    def isSufficient(self,cardsToTake):
        """ Checks if there are enough cards in deck to take from it
        :return Boolean"""
        if cardsToTake >= len(self.cards):
            return False
        else:
            return True

from cards import Card, suits
import random
# encoding=utf8
#TODO może będzie coś w stylu createFunctionalCards w klasie deck narazie i będzie się odpalać po stworzeniu talii?

class Deck(object):
    """ Deck class is build from 54 Cards objects"""
    def __init__(self,rules):
        self.cards = []
        self.build(rules)

    def build(self,rules):
        """Builds new deck from cards"""
        for s in suits:
            for v in range(1,14):
                self.cards.append(Card(s,v))
        if 'joker' in rules['functional_cards']:
            for j in range(2):
                self.cards.append(Card("Joker","Joker",True,True))

    def show(self):
        """For testing purposes"""
        print("Talia wygląda tak:")
        for c in self.cards:
            c.show()

    def shuffle(self):
        """ Shuffles created deck"""
        for i in range(len(self.cards)-1,0,-1):
            r = random.randint(0,i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def drawCard(self):
        return self.cards.pop()

    def isSufficient(self,cardsToTake):
        """ Checking if there's enough cards in deck to take from it"""
        if cardsToTake >= len(self.cards):
            return False
        else:
            return True

    #To będzie bardzo pomocna funkcja ale niekoniecznie w decku, bardziej w ręce
    def findById(self,id):
        for card in self.cards:
            if card.id == id:
                return card
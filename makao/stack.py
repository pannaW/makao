# encoding=utf8
from makao.cards import Card, suits

class Stack(object):
    def __init__(self,deck):
        self.cards = []
        self.drawFistCard(deck)

    def drawFistCard(self,deck):
        """ Draws first card until it is not functional """
        self.cards.append(deck.drawCard())
        while self.cards[-1] in functionalCards:
            self.drawFistCard(deck)

    def getTopCard(self):
        """ Returns top card
        :return Card object """
        return self.cards[-1]


    def addToStack(self,pickedCards):
        """ Adds cards picked by user from his hand
        :param list of card Objects"""
        self.cards.extend(pickedCards)

    def addToDeck(self,deck):
        """ Adding cards from stack to deck
         :return Deck object """
        for card in self.cards[:-1]:
            if card.joker:
                card.ResetToJoker()
        deck.cards.extend(self.cards[:-1])
        deck.shuffle()
        del self.cards[:-1]
        return deck


valiantCards = [Card(*[s, v, 0]) for v in (2, 3) for s in suits] + [Card(s, 13, 0) for s in ("Wino","Czerwo")]
demandCards = [Card(*[s, v,0]) for v in (1, 11) for s in suits]
delayCards = [Card(*[s, 4, 0]) for s in suits]
jokerCards = [Card(*["Joker", 0, 0] )]
functionalCards = delayCards + demandCards + valiantCards + jokerCards
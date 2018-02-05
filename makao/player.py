# encoding=utf8


class Player(object):
    """ Class Player """
    def __init__(self,name,soul=True):
        """
        Creating Class Player
        :param name: Name of player
        :param soul: Computers lack soul, humans are said to have it
        """
        self.name = name
        self.hand = []
        self.pickedCards = []
        self.soul = soul
        self.delay = 0

    def pickCard(self,index):
        """ Finds card in player's hand by card index and move it to player's 'pickedCards' list """
        self.pickedCards.append(self.hand.pop(index))

    def cancelPickedCards(self):
        """ Adds all picked cards back to the hand """
        self.hand.extend(self.pickedCards)
        self.pickedCards = []

    def draw(self,deck):
        """ Player draws the card
         :return Card object """
        newCard = deck.drawCard()
        self.hand.append(newCard)
        return newCard

    def takePunishement(self, PunishementValue, deck):
        """ Player take punishment from valiant cards """
        i = 0
        while i < PunishementValue:
            self.draw(deck)
            i += 1
        return self

    def removeCards(self):
        """ Player flushes cards pending in 'picked cards' list """
        self.pickedCards = []

    def emptyHand(self):
        """ checks if player still has cards in hand
        :return Boolean"""
        if not self.hand:
            return True
        else:
            return False

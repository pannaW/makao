# encoding=utf8


class Player(object):
    """ Class Player """
    def __init__(self,name,soul=False):
        """
        Creating Class Player
        :param name: Name of player
        :param soul: Computers lack soul, humans are said to have it
        """
        self.name = name
        self.hand = []
        self.soul = soul
        self.delay = 0

    def draw(self,deck):
        newCard = deck.drawCard()
        self.hand.append(newCard)
        return newCard

    def showHand(self):
        for card in self.hand:
            card.show()

    def removeCards(self,cardsList):
        for card in cardsList:
            self.hand.remove(card)

    def emptyHand(self):
        if not self.hand:
            return True
        else:
            return False

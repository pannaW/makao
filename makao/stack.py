# encoding=utf8

class Stack(object):                        # Czy stack napewno powinien być osobnym obiektem?
    """ Stack on the middle of the board """
    def __init__(self,card):
        """
        Creating the stack on the middle of the board
        """
        self.cards = []
        self.cards.append(card)

    def getTopCard(self):
        return self.cards[-1].show()

    def show(self):
        """For testing purposes"""
        for c in self.cards:
            c.show()

    def receive(self,pickedCards):
        """
        Odbieranie kart które użytkownik rzucił na stos
        :param pickedCards: lista kart które użytkownik chce rzucić na stos
        :return:
        """
        #TODO: jeśli valiant_cards_1 to jeśli valiant_cards to tylko jeśli topCard.value == firstCard.value
        #TODO: jeśli valiant_cards_3 to jeśli valiant_cards to firstCard.value musi być > topCard.value
        #TODO jeśli stan[asŻądanie], to walidacja tylko jeśli firstCard pasuje kolorem do stan[wartosc]; wyzeruj stan
        #TODO jeśli stan[jackŻądanie], to walidacja tylko jeśli firstCard

        firstCard, topCard = pickedCards[0], self.getTopCard
        if firstCard.suit == topCard.suit or firstCard.value == topCard.value or firstCard.value == "Joker":
            self.cards.extend(pickedCards)
            return True
        else:
            print("Niestety! Wybrana karta nie pasuje do karty na wierzchu stosu.")
            return False

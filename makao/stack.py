# encoding=utf8

class Stack(object):
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

    def receive(self,pickedCards, state):
        """
        Odbieranie kart które użytkownik rzucił na stos
        :param pickedCards: lista kart które użytkownik chce rzucić na stos
        :return:
        """
        #TODO: jeśli valiant_cards_1 to jeśli valiant_cards to tylko jeśli topCard.value == firstCard.value
        #TODO: jeśli valiant_cards_3 to jeśli valiant_cards to firstCard.value musi być > topCard.value
        #TODO jeśli stan[asŻądanie], to walidacja tylko jeśli firstCard pasuje kolorem do stan[wartosc]; wyzeruj stan
        #TODO jeśli stan['joker'], to walidacja tylko jeśli pasuje kolorem lub wartością
        #chyba zmieniłam zdanie i tu będziemy sprawdzać tylko jeśli as lub joker na wierzchu,a takto będzie inna funkcja
        firstCard, topCard = pickedCards[0], self.cards[-1]

        if state['type'] == 'jackDemand':
            if firstCard.value == state['value'] or firstCard.value == 11:
                self.cards.extend(pickedCards)
                return True
            else:
                print("Niestety! Wybrana karta nie spełnia wymagań żądania Waleta.")
                return False

        if state['type'] == 'joker':
            if firstCard.suit == state['suit'] or firstCard.value == state['value']:
                self.cards.extend(pickedCards)
                return True
            else:
                print("Niestety! Wybrana karta nie pasuje do tego Jokera.")
                return False

        if state['type'] == 'aceDemand':
            if firstCard.suit == state['suit'] or firstCard.value == 1:
                self.cards.extend(pickedCards)
                return True
            else:
                print("Niestety! Wybrana karta nie spełnia wymagań żądania Asa.")
                return False

        if firstCard.suit == topCard.suit or firstCard.value == topCard.value or firstCard.value == "Joker":
            self.cards.extend(pickedCards)
            return True
        else:
            print("Niestety! Wybrana karta nie pasuje do karty na wierzchu stosu.")
            return False

# encoding=utf8
from cards import Card, suits

class Stack(object):
    """ Stack on the middle of the board """
    def __init__(self,card):
        """ Creating the stack on the middle of the board """
        self.cards = []
        self.cards.append(card)

    def getTopCard(self):
        """ Shows top card """
        return self.cards[-1].show()

    def show(self):
        """Rather for testing purposes"""
        print("Stos wygląda tak:")
        for c in self.cards:
            c.show()

    def receive(self,pickedCards, state, rules):
        """
        Odbieranie kart które użytkownik rzucił na stos
        :param pickedCards: lista kart które użytkownik chce rzucić na stos
        :return:
        """
        firstCard, topCard = pickedCards[0], self.cards[-1]

        if state['type'] == 'valiant':
            if firstCard in valiantCards:
                if rules['valiant_cards'] == 1:
                    if firstCard.value == topCard.value:
                        self.cards.extend(pickedCards)
                        return True
                    else:
                        print("Niestety! Zasady zabraniają użycia kart walecznych o innej figurze niż ta na stosie")
                        return False

                if rules['valiant_cards'] == 2:
                    if firstCard.value == topCard.value:
                        self.cards.extend(pickedCards)
                        return True
                    elif firstCard.suit == topCard.suit:
                        self.cards.extend(pickedCards)
                        return True
                    else:
                        print("Niestety! Pierwsza karta nie jest w tym samym kolorze co ta na wierzchu!")
                        return False

                if rules['valiant_cards'] == 3:
                    if firstCard.value == topCard.value:
                        self.cards.extend(pickedCards)
                        return True
                    elif firstCard.suit == topCard.suit:
                        if firstCard.value > topCard.value:
                            self.cards.extend(pickedCards)
                            return True
                        else:
                            print("Niestety! Zgodnie z zasadami, karty muszą mieć wyższą wartość niż ta na wierzchu stosu")
                            return False
                    else:
                        print("Niestety! Pierwsza karta nie jest w tym samym kolorze co ta na wierzchu!")
                        return False

            else:
                print("Niestety! Podana karta musi być waleczna!")
                return False

        if state['type'] == 'delay':
            if firstCard.value == 4:
                self.cards.extend(pickedCards)
                return True
            else:
                print("Niestety! Potrzebna jest 4.")
                return False

        if state['type'] == 'jackDemand':
            if firstCard.value == state['value'] or firstCard.value == 11:
                self.cards.extend(pickedCards)
                return True
            else:
                print("Niestety! Wybrana karta nie spełnia wymagań żądania Waleta.")
                return False

        if state['type'] == 'aceDemand':
            if firstCard.suit == state['value'] or firstCard.value == 1:
                self.cards.extend(pickedCards)
                return True
            else:
                print("Niestety! Wybrana karta nie spełnia wymagań żądania Asa.")
                return False

        if firstCard.suit == topCard.suit or firstCard.value == topCard.value:
            self.cards.extend(pickedCards)
            return True
        else:
            print("Niestety! Wybrana karta nie pasuje do karty na wierzchu stosu.")
            return False

    def addToDeck(self,deck):
        """ Adding cards from stack to deck """
        for card in self.cards[:-1]:
            if card.joker:
                card.ResetToJoker()
        deck.cards.extend(self.cards[:-1])
        deck.shuffle()
        del self.cards[:-1]
        return deck

valiantCards = [Card(*[s, v, False]) for v in (2, 3) for s in suits] + [Card(s, 13,False) for s in ("Wino","Czerwo")]
demandCards = [Card(*[s, v, False]) for v in (1, 11) for s in suits]
delayCards = [Card(*[s, 4, False]) for s in suits]
functionalCards = delayCards + demandCards + valiantCards

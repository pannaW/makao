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


# c1 = {'suit':'hearts', 'value':12}
# c2 = {'suit':'clubs', 'value':13}
# c3 = {'suit':'spades', 'value':12}
# card_set = [c1,c2,c3]
#
# stack = []
# s1 = {'suit': 'diamonds', 'value': 4}
# s2 = {'suit':'hearts', 'value':4}
# stack = [s1,s2]
#
# firstCard = card_set[0]

#
# def receive(firstCard,stack,rest=[]):
#     if firstCard['suit'] == stack[-1]['suit'] or firstCard['value'] == stack[-1]['value']:
#         if rest:
#             if all(card['value'] == firstCard['value'] for card in rest):
#                 stack.append(firstCard)
#                 stack.extend(rest)
#                 print("Brawo! Wszystkie karty pasują! Stos wygląda teraz tak:")
#                 print(stack)
#             else:
#                 print("Błąd! Pozostałe karty nie mają tej samej figury co pierwsza!")
#                 print(stack)
#         else:
#             stack.append(firstCard)
#             print("Brawo! Stos wygląda teraz tak:")
#             print(stack)
#     else:
#         print("Niestety! Wybrana karta nie pasuje do karty na wierzchu stosu")
#         print(stack)
#
# receive(firstCard,stack,card_set[1:])

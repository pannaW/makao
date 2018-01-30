# def jackDemand(self,demander):
#     turn = self.prepareOrder(demander)
#     for player in turn:
#         self.turn(player)
#     self.state.clear()
#     return
#
# def prepareOrder(self,currentPlayer):
#     """Prepares players order for jack demand. Starts with player after demander and goes through all players
#     all the way around until it gets to demander"""
#     currentPlayerIndex = self.players.index(currentPlayer)
#     playerIndex = 0
#     turn = self.players
#
#     while playerIndex <= currentPlayerIndex:
#         turn += [turn.pop(0)]
#         playerIndex += 1
#     return turn


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

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
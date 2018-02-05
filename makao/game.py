# encoding=utf8
from makao.stack import Stack, valiantCards, demandCards, delayCards, functionalCards
from makao.deck import Deck
from makao.player import Player
import pickle


class Game(object):
    counter = 0
    currentPlayer = 0

    def __init__(self, players, rules):
        """ Initiate game object """
        self.rules = rules
        self.state = {'type': '', 'value': 0}
        self.deck = Deck(rules)
        self.deck.shuffle()
        self.winners = []
        self.players = players
        self.deal()
        self.stack = Stack(self.deck)

    def setCurrentPlayer(self):
        """ Set new current player accoring to counter """
        self.currentPlayer = self.players[self.counter % len(self.players)]

    def isCurrentPlayerSkipping(self):
        """ Checks if player is skipping turn. Decrements skipped turn counter in that case.
        :return Boolean """
        if self.currentPlayer.delay:
            self.currentPlayer.delay -= 1
            return True
        else:
            return False

    def nextPlayer(self):
        """Checks if player won, count down jackDemand if active, increments game counter."""

        if self.currentPlayer.emptyHand():
            self.addToWinners(self.currentPlayer)

        if self.state['type'] == 'jackDemand':
            self.state['demandTurns'] -= 1

        self.counter += 1
        return

    def jackDemandEndCondition(self):
        """ Check if jack demand state is over. Resets state in that case. """
        if self.state['type'] == 'jackDemand':
            if self.state['demandTurns'] == 0:
                self.resetState()

    def deal(self):
        """ Splits 5 cards to each player """
        for i in range(5):
            for player in self.players:
                player.draw(self.deck)

    def resetState(self):
        """ Resets game state """
        self.state = {'type': '', 'value': 0}

    def isEnd(self):
        """ Check if game is over
         :return Bolean """
        if self.rules['end_game'] == 1:
            if len(self.players) < 2:
                return True
        elif self.rules['end_game'] == 2:
            if self.winners:
                return True
        else:
            return False

    def resetJokers(self,pickedCards):
        """ Resets all renamed jokers again to jokers"""
        for card in pickedCards:
            if card.joker:
                card.ResetToJoker()

    def checkPickedCards(self,pickedCards):
        """ Checks if (1) Cards were picked, (2) have the same value, (3) more than 2 cards were picked (certain conditions)
            :param  (list) pickedCards
            :return (string) error message / (list) pickedCards
        """

        if pickedCards:
            if all(card.value == pickedCards[0].value for card in pickedCards):
                if self.rules['putting_cards'] == 1:
                    if len(pickedCards) != 2 or self.state['type'] == 'jackDemand':
                        return pickedCards
                    else:
                        error = "Zasady zabraniają wyrzucania 2 kart!"
                        return error
                else:
                    return pickedCards
            else:
                error = "Karty powinny być tej samej figury!"
                return error
        else:
            error = "Nie wybrałeś kart!"
            return error

    def matchWithTopCard(self, pickedCards):
            """
            Conditions over cards match, considers all game states
            :param pickedCards: cards intended to be add to stack
            :return: (Boolean) True / (str) error message
            """
            firstCard, topCard = pickedCards[0], self.stack.cards[-1]
            #1. If Queen Spades

            if 'queen' in self.rules['functional_cards']:
                if len(pickedCards) == 1:
                    if firstCard.value == 12 and firstCard.suit == 'Wino':
                        self.resetState()
                        return True

                if topCard.value == 12 and topCard.suit == 'Wino':
                    return True

            #2. If valiant state
            if self.state['type'] == 'valiant':
                if firstCard in valiantCards:
                    if self.rules['valiant_cards'] == 1:
                        if firstCard.value == topCard.value:
                            return True
                        else:
                            error = "Niestety! Zasady zabraniają użycia kart walecznych o innej figurze niż ta na stosie"
                            return error

                    if self.rules['valiant_cards'] == 2:
                        if firstCard.value == topCard.value:
                            return True
                        elif firstCard.suit == topCard.suit:
                            return True
                        else:
                            error = "Niestety! Pierwsza karta nie jest w tym samym kolorze co ta na wierzchu!"
                            return error

                    if self.rules['valiant_cards'] == 3:
                        if firstCard.value == topCard.value:
                            return True
                        elif firstCard.suit == topCard.suit:
                            if firstCard.value > topCard.value:
                                return True
                            else:
                                error = "Niestety! Zgodnie z zasadami, karty muszą mieć wyższą wartość niż ta na wierzchu stosu"
                                return error
                        else:
                            error = "Niestety! Pierwsza karta nie jest w tym samym kolorze co ta na wierzchu!"
                            return error

                else:
                    error = "Niestety! Podana karta musi być waleczna!"
                    return error

            #3. if delay state
            if self.state['type'] == 'delay':
                if firstCard.value == 4:
                    return True
                else:
                    error = "Niestety! Potrzebna jest 4."
                    return error
            #4. if jackDemand state
            if self.state['type'] == 'jackDemand':
                if firstCard.value == self.state['value'] or firstCard.value == 11:
                    return True
                else:
                    error = "Niestety! Wybrana karta nie spełnia wymagań żądania Waleta."
                    return error
            #5. if aceDemand state
            if self.state['type'] == 'aceDemand':
                if firstCard.suit == self.state['value'] or firstCard.value == 1:
                    self.resetState()
                    return True
                else:
                    error = "Niestety! Wybrana karta nie spełnia wymagań żądania Asa."
                    return error
            #6. regular match
            if firstCard.suit == topCard.suit or firstCard.value == topCard.value:
                return True
            else:
                error = "Niestety! Wybrana karta nie pasuje do karty na wierzchu stosu."
                return error

    def isFunctional(self, cardList):
        """ Modifies state accordingly if cards are functional
        :return str "Jack"/"Ace" in case it is a demand card """
        for card in cardList:
            if card in delayCards:
                self.state['type'] = 'delay'
                self.state['value'] += 1
            if card in valiantCards:
                self.state['type'] = 'valiant'
                if card.value == 13:
                    self.state['value'] += 5
                else:
                    self.state['value'] += card.value
            if card in demandCards:
                if card.value == 1:
                    return "Ace"
                elif card.value == 11:
                    return "Jack"
        return

    def addToWinners(self,player):
        """ Move from players list to winners list """
        self.winners.append(self.players.pop(self.players.index(player)))

    def pickCards(self,card_indexes):
        """Finds cards in players hand by indexes list
        :return list of Card objects
        """
        pickedCards = []
        for i in card_indexes:
            i = int(i)
            pickedCards.append(self.currentPlayer.hand[i])
        return pickedCards

    def showCompetitors(self):
        """ Finds player's competitors
        :return list of Player objects """
        competitors = []
        for player in self.players:
            if player != self.currentPlayer:
                competitors += [player]
        return competitors

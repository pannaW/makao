# encoding=utf8
from makao.stack import Stack, valiantCards, demandCards, delayCards, functionalCards
from makao.deck import Deck
from makao.player import Player
import pickle


class Game(object):
    counter = 0
    currentPlayer = 0

    def __init__(self, players, rules):
        self.rules = rules
        self.state = {'type': '', 'value': 0}
        self.deck = Deck(rules)
        self.deck.shuffle()
        self.winners = []
        self.players = players
        self.deal()
        self.stack = Stack(self.deck)

    def setCurrentPlayer(self):
        self.currentPlayer = self.players[self.counter % len(self.players)]

    def isCurrentPlayerSkipping(self):
        if self.currentPlayer.delay:
            self.currentPlayer.delay -= 1
            return True
        else:
            return False

    def nextPlayer(self):
        """Checks if player won, count down jackDemand if active,
           add to the game counter (-> next player) """

        if self.currentPlayer.emptyHand():
            self.addToWinners(self.currentPlayer)

        if self.state['type'] == 'jackDemand':
            self.state['demandTurns'] -= 1

        self.counter += 1
        return

    def jackDemandEndCondition(self):
        if self.state['type'] == 'jackDemand':
            if self.state['demandTurns'] == 0:
                self.resetState()

    def deal(self):
        """ Splitting 5 cards to each player """
        for i in range(5):
            for player in self.players:
                player.draw(self.deck)

    def resetState(self):
        """ Resets game state """
        self.state = {'type': '', 'value': 0}

    def isEnd(self):
        """ Check if game is over """
        if self.rules['end_game'] == 1:
            if len(self.players) < 2:
                return True
        elif self.rules['end_game'] == 2:
            if self.winners:
                return True
        else:
            return False

    def turn(self, player):
        """Single player's turn """
        print("\n--------------------------------------------------------------\n"
              "Gra gracz: %s" % player.name)

        self.jackDemandEndCondition()

        if player.delay:
            player.delay -= 1
            print("Tracisz kolejkę. Pozostało %d kolejek do czekania" % player.delay)
            return

        else:
            self.choose(player)
            print("Po Twoim ruchu sytuacja wygląda tak:")
            self.renderPlayerView(player)
            print(self.state)
            return




    def resetJokers(self,pickedCards):
        for card in pickedCards:
            if card.joker:
                # print("Zmieniamy Twoją kartę z powrotem na Jokera\n")
                card.ResetToJoker()

    def choose(self, player):
        """Expect user to choose put or take"""
        self.renderPlayerView(player)
        print(self.state)

        while True:
            action = input("Wybierz: 'put' or 'take'\n")
            if action == 'put':
                pickedCards = self.checkPickedCards(self.letUserPickCardsToPut(player))
                if pickedCards:
                    if self.matchWithTopCard(pickedCards):
                        self.isFunctional(pickedCards)
                        break
                    else:
                        self.resetJokers(pickedCards)
                        print("Co chcesz zrobić?")
                else:
                    self.resetJokers(pickedCards)
            elif action == 'take':
                if self.state['type'] == 'delay':
                    player.delay = self.state['value']
                    print("{} tracisz {} kolejek".format(player.name, self.players[self.players.index(player)].delay))
                    self.resetState()
                    break
                if self.state['type'] == 'valiant':
                    if not self.deck.isSufficient(self.state['value']):
                        self.stack.addToDeck(self.deck)
                    player.takePunishement(self.state['value'],self.deck)
                    self.resetState()
                    break
                else:
                    if not self.deck.isSufficient(2):
                        self.stack.addToDeck(self.deck)
                    self.take(player)
                    break


    def checkPickedCards(self,pickedCards):
        """ Walidacja wybranych kart:
                czy podał karty
                    określ wartość i figurę
                czy są tej samej figury
                czy można wyrzucić dwie karty
                    czy nie ma dwóch kart
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
        """ Modifies state accordingly if cards are functional """
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

    def take(self):
        """Dobieranie jednej karty
            +Walidacja wyrzucanych kart"""
        #Musiałam zrobić prawie kalkę części "put" w Choose; może da się to jakoś zmienić w funkcję

        #zapisuję do listy,bo validate powinno przyjmować listę
        newCard = self.currentPlayer.draw(self.deck)
        pickedCards = []
        pickedCards.append(newCard)

        print("Nowa karta:")
        newCard.show()

        if self.rules['taking_cards'] == 2:
            answer = input("Chcesz wyrzucić nową kartę? (t/n)")
            if answer == 't':
                if self.matchWithTopCard(pickedCards):
                    self.isFunctional(pickedCards)
                else:
                    self.resetJokers(pickedCards)

        if self.rules['taking_cards'] == 3:
            answer = input("Chcesz wyrzucić nową kartę? (t/n)")
            if answer == 't':
                pickedCards.extend(self.letUserPickCardsToPut(self.currentPlayer))
                pickedCards = self.checkPickedCards(pickedCards)
                if pickedCards:
                    if self.matchWithTopCard(pickedCards):
                        self.isFunctional(pickedCards)
                    else:
                        self.resetJokers(pickedCards)
                else:
                    self.resetJokers(pickedCards)
        return

    def addToWinners(self,player):
        """ Move from players list to winners list"""
        self.winners.append(self.players.pop(self.players.index(player)))

    def pickCards(self,card_indexes):
        pickedCards = []
        for i in card_indexes:
            i = int(i)
            pickedCards.append(self.currentPlayer.hand[i])
        return pickedCards

    def letUserPickCardsToPut(self,player):
        """Temporary function"""
        card_indexes = [int(x) for x in input("Jakie karty chcesz wyrzucić?\n").split()]
        pickedCards = []
        for i in card_indexes:
            pickedCards.append(player.hand[i])
        return pickedCards

    def showCompetitors(self):
        competitors = []
        for player in self.players:
            if player != self.currentPlayer:
                competitors += [player]
        return competitors

    def renderPlayerView(self,player):
        """Shows top card, player's cards and competitors cards amount"""
        #TODO:
        # competitors = list(set(self.players) - set(list(player)))
        # return {
        #     'top_card': self.stack.getTopCard(),
        #     'deck_len': len(self.deck.cards),
        #     'hand': player.showHand(),               #pewnie będzie w terminalu zamiast tu więc trzeba później zmienić
        #     'competitors': competitors
        #     }
        #

        print("Karta środka to:")
        self.stack.getTopCard()
        print("\nW talii zostało %d kart\n" % len(self.deck.cards))
        print("Oto Twoje karty.")
        player.showHand()
        for competitor in self.players:
            if competitor != player:
                print("Twój przeciwnik: {} ma {} kart".format(competitor.name, len(competitor.hand)))
        return

    def go(self):
        while not game.isEnd():
            self.currentPlayer = self.players[self.counter%len(self.players)]
            self.turn(self.currentPlayer)
            self.nextPlayer()

        return self.winners


player1 = Player("Bob")
player2 = Player("Dylan")
player3 = Player("Ann")
player4 = Player("Scott")

players_list = [player1, player2,player3]

rules_list = {
        'putting_cards': 2,
        'taking_cards': 3,
        'functional_cards': ['queen', 'joker'],
        'end_game': 1,
        'valiant_cards': 2
        }

game = Game(players_list, rules_list)

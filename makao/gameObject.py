# encoding=utf8
from stack import Stack, valiantCards, demandCards, delayCards, functionalCards
from deck import Deck
from player import Player


class Game(object):
    currentPlayerId = 0
    def __init__(self, players, rules):
        self.rules = rules
        self.state = {'type': '', 'value': 0}
        self.deck = Deck(rules)
        self.deck.shuffle()
        self.winners = []
        self.players = players
        self.deal()
        self.stack = Stack(self.deck.drawCard())
        self.i = 0

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
                return 1
        elif self.rules['end_game'] == 2:
            if self.winners:
                return 2
        else:
            return False

    def turn(self, player):
        """Single player's turn """
        self.currentPlayer = player

        print("Gra gracz: %s" % player.name)

        if player.delay:
            player.delay -= 1
            print("Tracisz kolejkę. Pozostało %d kolejek do czekania" % player.delay)
            return True

        else:
            self.renderPlayerView(player)
            print(self.state)

            if self.state['type'] == 'jackDemand':
                if player == self.state['demander']:
                    self.choose(player)
                    self.resetState()
                else:
                    self.choose(player)
            else:
                self.choose(player)

        # po wyrzuceniu sprawdzam czy ma jeszcze karty
            if player.emptyHand():
                print("Dodaję Cię do zwycięzców!")
                self.addToWinners(player)
                return False

            print("Po Twoim ruchu sytuacja wygląda tak:")
            self.renderPlayerView(player)
            print(self.state)
            return True

    def choose(self, player):
        """Expect user to choose put or take"""
        while True:
            action = input("Wybierz: 'put' or 'take'\n")
            if action == 'put':
                pickedCards = self.put(self.letUserPickCardsToPut(player))
                if pickedCards:
                    if self.matchWithTopCard(pickedCards, player):  #TODO dama wino
                        if self.state['type'] == 'aceDemand':  # narazie droga na okrętkę;
                            self.resetState()  # bo to się flushuje po pierwszym dopasowaniu;
                        self.isFunctional(pickedCards, player)
                        print(self.state)
                        break
                    else:
                        for card in pickedCards:
                            if card.joker:
                                print("Zmieniamy Twoją kartę z powrotem na Jokera\n")
                                card.ResetToJoker()
                        print("Co chcesz zrobić?")
                else:
                    for card in pickedCards:
                        if card.joker:
                            print("Zmieniamy Twoją kartę z powrotem na Jokera\n")
                            card.ResetToJoker()
            elif action == 'take':
                if self.state['type'] == 'delay':
                    player.delay = self.state['value']
                    print("Nie bierzesz kart, ale tracisz %d kolejek" % self.players[self.players.index(player)].delay)
                    self.resetState()
                    break
                if self.state['type'] == 'valiant':
                    # sprawdzenie czy wystarczy kart w decku
                    if not self.deck.cards or not self.deck.isSufficient(self.state['value']):
                        self.stack.addToDeck(self.deck)
                    # weź karty kary (żadne dokładki nie są tu możliwe) zresetuj stan
                    player.takePunishement(self.state['value'],self.deck)
                    self.resetState()
                    break
                else:
                    # sprawdzenie czy wystarczy kart w decku
                    if len(self.deck.cards) < 2:
                        self.stack.addToDeck(self.deck)
                    self.take(player)
                    break

    def put(self,pickedCards):
        """ Walidacja wybranych kart:
                czy podał karty
                czy karta jest Jokerem (SPRAWDZA KAŻÐĄ KARTĄ)
                    określ wartość i figurę
                czy są tej samej figury
                czy można wyrzucić dwie karty
                    czy nie ma dwóch kart
            :param  player      object
            :return pickedCards list
        """

        if pickedCards:
            for card in pickedCards:
                if card.value == "Joker":
                    answer = list()
                    answer += [input("Jakiego koloru ma być ten Joker?")]
                    answer += [int(input("Jakiej figury ma być ten Joker?"))]
                    card.rename(*answer)

            if all(card.value == pickedCards[0].value for card in pickedCards):
                if self.rules['putting_cards'] == 1:
                    if len(pickedCards) != 2 or self.state['type'] == 'jackDemand':
                        return pickedCards
                    else:
                        print("Zasady zabraniają wyrzucania 2 kart!")
                        return []
                else:
                    return pickedCards
            else:
                print("Karty powinny być tej samej figury!")
                return []
        else:
            print("Nie wybrałeś kart!")
            return []

    def matchWithTopCard(self, pickedCards, player):
        result = self.stack.receive(pickedCards, self.state, self.rules)
        if result:
            player.removeCards(pickedCards)
            return True
        else:
            return False

    def isFunctional(self, cardList,currentPlayer):
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
                    self.state['type'] = 'aceDemand'
                    self.state['value'] = input("Jakiego koloru żądasz?")
                    print(self.state)
                    return
                elif card.value == 11:
                    self.state['type'] = 'jackDemand'
                    self.state['value'] = int(input("Jakiej karty żądasz?"))
                    self.state['demander'] = currentPlayer
                    print(self.state)
                    return
        print(self.state)
        return

    def take(self,player):
        """Dobieranie jednej karty
            +Walidacja wyrzucanych kart"""
        #Musiałam zrobić prawie kalkę części "put" w Choose; może da się to jakoś zmienić w funkcję

        #zapisuję do listy,bo receive powinno przyjmować listę
        newCard = player.draw(self.deck)
        pickedCards = []
        pickedCards.append(newCard)

        print("Nowa karta:")
        newCard.show()
        print("Wszystkie karty:")
        player.showHand()
        if self.rules['taking_cards'] == 2:
            answer = input("Chcesz wyrzucić nową kartę? (t/n)")
            if answer == 't':
                if self.matchWithTopCard(pickedCards, player):
                    if self.state['type'] == 'aceDemand':
                        self.resetState()
                    self.isFunctional(pickedCards, player)
                else:
                    if pickedCards[0].joker:
                        print("Zmieniamy Twoją kartę z powrotem na Jokera\n")
                        pickedCards[0].ResetToJoker()
                return

        if self.rules['taking_cards'] == 3:
            answer = input("Chcesz wyrzucić nową kartę? (t/n)")
            if answer == 't':
                pickedCards.extend(self.letUserPickCardsToPut(player))
                pickedCards = self.put(pickedCards)
                if pickedCards:
                    if self.matchWithTopCard(pickedCards, player):  # TODO dama wino
                        if self.state['type'] == 'aceDemand':  # narazie droga na okrętkę;
                            self.resetState()  # bo to się flushuje po pierwszym dopasowaniu;
                        self.isFunctional(pickedCards, player)
                        return
                    else:
                        for card in pickedCards:
                            if card.joker:
                                print("Zmieniamy Twoją kartę z powrotem na Jokera\n")
                                card.ResetToJoker()
                        return
                else:
                    for card in pickedCards:
                        if card.joker:
                            print("Zmieniamy Twoją kartę z powrotem na Jokera\n")
                            card.ResetToJoker()
                    return
            else:
                return
        else:
            return

    #UWAGA: TakePunishement przesunięte do Playera
    #UWAGA: sufficentDeck przesunięte do Decka
    # UWAGA: addToDeck przesunięte do Stacka

    def addToWinners(self,player):
        """ Move from players list to winners list"""
        self.winners.append(self.players.pop(self.players.index(player)))

    def letUserPickCardsToPut(self,player):
        """Temporary function"""
        card_indexes = [int(x) for x in input("Jakie karty chcesz wyrzucić?\n").split()]
        pickedCards = []
        for i in card_indexes:
            pickedCards.append(player.hand[i])
        return pickedCards


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
            if self.currentPlayerId == len(self.players):
                self.currentPlayerId = 0

            self.turn(self.players[self.currentPlayerId])
            self.currentPlayerId += 1

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

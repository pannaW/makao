# encoding=utf8
from stack import Stack
from deck import Deck
from player import Player
from cards import Card, suits

player1 = Player("Bob",True)
player2 = Player("Dylan",True)
player3 = Player("Ann",True)
player4 = Player("Scott", True)

players_list = [player1, player2,player3,player4]

rules_list = {
        'putting_cards' : 2,
        'taking_cards' : 3,
        'functional_cards' : ['queen', 'joker'],
        'end_game' : 1,
        'valiant_cards' : 2
        }


class Game(object):
    def __init__(self, players, rules):
        self.rules = rules
        self.state = {'type': '', 'value': 0}
        self.deck = Deck(rules['functional_cards'])
        self.deck.shuffle()
        self.winners = []
        self.players = players
        self.deal()
        self.stack = Stack(self.deck.drawCard())

    def deal(self):
        """ Splitting 5 cards to each player """
        for i in range(5):
            for player in self.players:
                player.draw(self.deck)

    def addToDeck(self):
        """ Adding cards to deck if it's empty or doesn't have sufficient amount of cards"""
        if not self.deck.cards or not self.sufficentDeck():
            self.deck.cards.extend(self.stack.cards[:-1])
            self.deck.shuffle()
            del self.stack.cards[:-1]

    def countPlayers(self):
        """ Count number of players
        :return: int
        """
        return len(self.players)

    def sufficentDeck(self,cardsToTake):
        """ Checking if there's enough cards in deck to take from it"""
        if cardsToTake >= len(self.deck.cards):
            return False
        else:
            return True

    def turn(self, player):
        """Pojedynczy ruch gracza"""
        #TODO wersja robocza z tym false i z tym że to jest tutaj

        if self.rules['end_game'] == 1:
            if len(self.players) < 2:
                print("Koniec gry!")
                print("Wygrani:")
                for player in self.winners:
                    print(player.name)
                return False
        elif self.rules['end_game'] == 2:
            if self.winners:
                print("Koniec gry!")
                print("Wygrał:")
                print(self.winners[0].name)
                return False
        if self.state['type']:
                if self.state['type'] == 'delay':
                #jeśli gracz dołożył 4
                    #state['value'] += tyle ile było 4
                    #następny gracz (return True)
                #jeśli gracz ciągnie
                    #player.delay = state['value']
                    # self.state.clear()
                    # nastepny gracz (return True)
                if self.state['type'] == 'jackDemand':
                #if player == demander (pod warunkiem że tu mamy jakiegoś fora)
                    #self.state.clear()
                # normalne choose()
                #(return True)

                if self.state['type'] == 'valiant':
                #jesli gracz ciagnie
                    #sprawdz czy starczy kart w decku sufficientDeck(state['value'])
                    #petla ciagniecia tylu kart ile w state['value']
                    # self.state.clear()
                    #(return True)
                #jesli walczy (ciagnie)
                    #if rules['valiantCards'] == 1
                        # pozwol mu dorzucic tylko jesli ma tez valiantCard i to tej samej wartosci
                        # lub jeśli była zasada o damie, to moze nią skasować stan
                    #if rules['valiantCards'] == 2
                        # pozwol mu dorzucic tylko jesli ma tez valiantCard tego samego koloru (?pierwsza czy wszystkie?)
                        # lub jeśli była zasada o damie, to moze nią skasować stan
                    # if rules['valiantCards'] == 3
                        # pozwol mu dorzucic tylko jesli ma tez valiantCard tego samego koloru (?pierwsza czy wszystkie?) i o wartosci wyzszej niz TopCard
                        # lub jeśli była zasada o damie, to moze nią skasować stan
                    #state['value'] += tyle ile było kart
                    #następny gracz (return True)


        #sprawdzanie czy gracz nie ma opuścić kolejki;
        #TODO to chyba pójdzie wyżej do góry jako if nad state['type'] a to co wewnątrz będzie elsem do state['type']
        if player.delay == 0:
            self.presentSituation(player)
            self.choose(player)
            self.presentSituation(player)
        else:
            player.delay -= 1

    def letUserPickCardsToPut(self,player):
        """Temporary class"""
        card_indexes = [int(x) for x in input("Jakie karty chcesz wyrzucić?\n").split()]
        pickedCards = []
        for i in card_indexes:
            pickedCards.append(player.hand[i])
        return pickedCards


    def put(self,pickedCards):
        """ Walidacja wybranych kart:
                czy podał karty
                czy są tej samej figury
                czy można wyrzucić dwie karty
                    czy nie ma dwóch kart
            :param  player      object
            :return pickedCards list
        """

        if pickedCards:
            if all(card.value == pickedCards[0].value or card.value == "Joker" for card in pickedCards):
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

    def take(self,player):
        #narazie tak bo receive powinno przyjmować listę
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
                self.matchWithTopCard(pickedCards, player)
                return
        if self.rules['taking_cards'] == 3:
            answer = input("Chcesz wyrzucić nową kartę? (t/n)")
            if answer == 't':
                pickedCards.extend(self.letUserPickCardsToPut(player))
                print(pickedCards)
                if self.put(pickedCards):
                    self.matchWithTopCard(pickedCards,player)
                    return
                else:
                    return
            else:
                return
        return

    def isFunctional(self, cardList):
        for card in cardList:
            if card in delayCards:
                self.state['type'] = 'delay'
                self.state['value'] += 1
            if card in demandCards:
                if card.value == 1:
                    self.state['type'] = 'aceDemand'
                    self.state['value'] = input("Jakiego koloru żądasz?")
                elif card.value == 11:
                    self.state['type'] = 'jackDemand'
                    self.state['value'] = input("Jakiej karty żądasz?")
            if card in valiantCards:
                self.state['type'] = 'valiant'
                if card.value == 13:
                    self.state['value'] += 5
                else:
                    self.state['value'] += card.value
        if cardList[-1].value == "Joker":
            self.state['type'] = 'joker'
            self.state['suit'] = input("Jakiego koloru ma być ta karta?")
            self.state['value'] = input("Jakiej figury ma być ta karta?")
        return

    def presentSituation(self,player):
        """Shows top card, player's cards and competitors cards amount"""
        print("Karta środka to:")
        self.stack.getTopCard()
        print("Oto Twoje karty.")
        player.showHand()
        for competitor in self.players:
            if competitor != player:
                print("Twój przeciwnik: {} ma {} kart".format(competitor.name, len(competitor.hand)))
        return

    def choose(self,player):
        """Expect user to choose put or take"""
        while True:
            action = input("Wybierz: 'put' or 'take'\n")
            if action == 'put':
                pickedCards = self.put(self.letUserPickCardsToPut(player))
                if pickedCards:
                    if self.matchWithTopCard(pickedCards,player):
                        if player.emptyHand():
                            #przenieś tego gracza z graczy do zwycięzców
                            self.winners.append(self.players.pop(self.players.index(player)))
                        break
                    else:
                        print("Co chcesz zrobić?")
            elif action == 'take':
                #TODO sprawdź czy starczy kart w decku
                self.take(player)
                break

    def matchWithTopCard(self,pickedCards,player):
        result = self.stack.receive(pickedCards,self.state)
        if result:
            #narazie droga na okrętkę, w przeglądarce to będzie globalna zmienna sesyjna więc luz
            if self.state['type'] == 'joker' or self.state['type'] =='aceDemand':
                self.state.clear()
            player.removeCards(pickedCards)
            self.isFunctional(pickedCards)
            print(self.state)
            return True
        else:
            return False

    def jackDemand(self,demander):
        #TODO pytanie czy stan o jackDemandzie wjeżdża jeszcze pod koniec kolejki tego uzytkownika czy przy następnym;
        turn = self.prepareOrder(demander)
        for player in turn:
            self.turn(player)
        self.state.clear()
        return

    def prepareOrder(self,currentPlayer):
        """Prepares players order for jack demand. Starts with player after demander and goes through all players
        all the way around until it gets to demander"""
        currentPlayerIndex = self.players.index(currentPlayer)
        playerIndex = 0
        turn = self.players

        while playerIndex <= currentPlayerIndex:
            turn += [turn.pop(0)]
            playerIndex += 1
        return turn


game = Game(players_list, rules_list)


valiantCards = [Card(s, v) for v in (2, 3) for s in suits] + [Card(s, 13) for s in ("Spades", "Hearts")]
demandCards = [Card(s, v) for v in (1, 11) for s in suits]
delayCards = [Card(s, 4) for s in suits]
functionalCards = delayCards + demandCards + valiantCards
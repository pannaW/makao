# encoding=utf8
from stack import Stack
from deck import Deck
from player import Player
from cards import Card, suits

player1 = Player("Bob",True)
player2 = Player("Dylan",True)
player3 = Player("Ann",True)

players_list = [player1, player2, player3]

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
        #TODO check if previous player still have cards; if not, add to "winners"/end game
        #TODO check if at least two players still in game
        #sprawdzanie czy gracz nie ma opuścić kolejki;
        if player.delay == 0:
            #pokazuje mu karty
            print("Karta środka to:")
            self.stack.getTopCard()
            print("Oto Twoje karty.")
            player.showHand()

            #niech wybiera czy rzuca czy bierze; (dopóki akcja nie zakończy się powodzeniem)
            while True:
                action = input("Wybierz: 'put' or 'take'\n")
                if action == 'put':
                    pickedCards = self.put(player)
                    if pickedCards:
                        result = self.stack.receive(pickedCards)
                        if result:
                            player.removeCards(pickedCards)
                            self.isFunctional(pickedCards)
                            print(self.state)
                            #TODO sprawdź czy w dodanych kartach były karty kary lub opóźnienia, lub żądania
                            break
                elif action == 'take':
                    result = self.take(player)
                    if result:
                        break
            print("Twoje karty wyglądają teraz tak:")
            player.showHand()
            print("A stos tak:")
            self.stack.show()
        else:
            player.delay -= 1

    def put(self,player):
        """ Wykładanie kart
                Wczytuję karty podane przeez użytkownika;
                czy podał karty
                czy są tej samej figury
                czy można wyrzucić dwie karty
                    czy nie ma dwóch kart
            :param  player      object
            :return pickedCards list
        """

        #Wczytywanie kart wraz z walidacją
        card_indexes = [int(x) for x in input("Jakie karty chcesz wyrzucić?\n").split()]
        pickedCards = []
        for i in card_indexes:
            pickedCards.append(player.hand[i])

        #Walidacja
            #TODO ewentualnie sprawdzić jeszcze czy kart nie jest więcej niż 6 lub 4 jeśli nie ma jokerów
        if pickedCards:
            # ta linijka z Jokerem, nie wiem czy zadziała
            if all(card.value == pickedCards[0].value or card.value == "Joker" for card in pickedCards):
                #TODO chyba że jest jackDemand, wtedy powinno być wolno rzucać 2 karty
                if self.rules['putting_cards'] == 1:
                    if len(pickedCards) == 2:
                        print("Zasady zabraniają wyrzucania 2 kart!")
                        return []
                    else:
                        return pickedCards
                else:
                    return pickedCards
            else:
                print("Karty powinny być tej samej figury!")
                return []
        else:
            print("Nie wybrałeś kart!")
            return []

    def take(self,player):
        player.draw(self.deck)
        #jeśli zasada taking_cards = 1 to zakończ
        #jeśli zasada taking_cards = 2 to sprawdź czy stos akceptuje kartę
        #jeśli zasada taking_cards = 3 to sprawdź czy wybrana karta pasuje do pierwszej a potem czy stos akceptuje karte
        return True

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
                    self.state['counter'] = self.countPlayers()
            if card in valiantCards:
                self.state['type'] = 'valiant'
                if card.value == 13:
                    self.state['value'] += 5
                else:
                    self.state['value'] += card.value

game = Game(players_list, rules_list)

valiantCards = [Card(s, v) for v in (2, 3) for s in suits] + [Card(s, 13) for s in ("Spades", "Hearts")]
demandCards = [Card(s, v) for v in (1, 11) for s in suits]
delayCards = [Card(s, 4) for s in suits]
functionalCards = delayCards + demandCards + valiantCards
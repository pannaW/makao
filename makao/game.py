# encoding=utf8
from makao.stack import Stack, valiantCards, demandCards, delayCards, functionalCards
from makao.deck import Deck
from makao.cards import suits
from collections import Counter
import random


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

        if 'queen' in self.rules['functional_cards']:
            if len(cardList) == 1:
                if cardList[0].value == 12 and cardList[0].suit == 'Wino':
                    self.resetState()
                    return

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

    def computerStrategy(self):
        """ Computer player turn """

        possibleCards = []

        def getMostFrequentSuit():
            suitOccurance = Counter([card.suit for card in self.currentPlayer.hand])
            for (key, value) in suitOccurance.items():
                if value == max(suitOccurance.values()):
                    key = str(key)
                    #if only jokers in hand
                    if key == "Joker":
                        key = random.choice([suits])
                    return key

        def getMostFrequentValue():
            valueOccurance = Counter([card.value for card in self.currentPlayer.hand])
            for (key, value) in valueOccurance.items():
                if value == max(valueOccurance.values()):
                    key = int(key)
                    #if only jokers in hand
                    if key == 0:
                        key = random.choice(range(1,13))
                    return key


        def think():
            """
            if state is delay or valiant
                put just 1 card; return
            else
            1. if comp has functional cards in hand
                1.1 if other players have less than 3 cards
                        put (valiant,delay,demand); return
                1.2 if comp has more than 6 cards
                        if comp has possible delay cards
                        put it; return
                1.3 if comp has > 1 delay card
                        put: return
                1.4 if comp has > 1 valiant card
                        put: return
            2. comp has card set (if more than 2 cards has the same value as any of the possibleCards)
                    put return
            3. just put any card that is possible to put; return

            :return: A list of Card Objects chosen to be put on the stack
            """

            pickedCards = []

            possibleValiantCards = [cards for cards in possibleCards if cards in valiantCards]
            possibleDelayCards = [cards for cards in possibleCards if cards in delayCards]
            possibleDemandCards = [cards for cards in possibleCards if cards in demandCards]
            possibleJacks = [jacks for jacks in possibleDemandCards if jacks.value == 11]
            nonFunctionalCardsInHand = [cards for cards in self.currentPlayer.hand if
                                        cards not in functionalCards]
            ValiantCardsInHand = [cards for cards in self.currentPlayer.hand if
                                        cards in valiantCards]
            nonFunctionalCardsValues = [card.value for card in nonFunctionalCardsInHand]

            #Jokers, the last hope
            for card in possibleCards:
                #if a card is a joker
                if card.suit == "Joker":
                    #defaults
                    suit = getMostFrequentSuit()
                    value = self.stack.getTopCard().value

                    if self.state['type'] == 'valiant':
                        if self.rules['valiant_cards'] == 2:
                            if ValiantCardsInHand:
                                suit = ValiantCardsInHand[0].suit
                    elif self.state['type'] == 'jackDemand':
                        value = self.state['value']
                    elif self.state['type'] == 'aceDemand':
                        suit = self.state['value']
                        value = getMostFrequentValue()

                    card.renameJoker(suit,value)


            # if state is delay or valiant put only one card
            if self.state['type'] == 'valiant' or self.state['type'] == 'delay':
                pickedCards += [possibleCards[0]]
                return pickedCards
            #if state jack demand put more jacks first
            elif self.state['type'] == 'jackDemand':
                if possibleJacks:
                    if self.rules['putting_cards'] == 1:
                        # if there are 3 or 4 jacks, put all of them
                        if len(possibleJacks) > 2:
                            pickedCards += possibleJacks
                            return pickedCards
                        else:
                            # if there is 1 or 2 jacks, put only one
                            pickedCards += [possibleJacks[0]]
                            return pickedCards
                            # if it is allowed to put 2 cards, put all of them
                    else:
                        pickedCards += possibleJacks
                        return pickedCards
                # if no more jacks put as many cards as matches
                else:
                    pickedCards += possibleCards
                return pickedCards
            else:

                # 1.1 check if competitors have less than 3 cards
                competitors = self.showCompetitors()
                competitorsCardsCount = [len(competitor.hand) for competitor in competitors]
                if [count for count in competitorsCardsCount if count < 3]:
                    # 1.1.1 check if computer has valiant cards
                    if possibleValiantCards:
                        pickedCards += [possibleValiantCards[0]]
                        return pickedCards
                    # 1.1.2 check if computer has delay cards
                    elif possibleDelayCards:
                        pickedCards += [possibleDelayCards[0]]
                        return pickedCards
                    # 1.1.3 check if computer has demand cards
                    elif possibleDemandCards:
                        # 1.1.3.1 check if jacks in possible to put demand cards
                        if possibleJacks:
                            # if there are more than 1 card sets non-funtional cards
                            if len(set(nonFunctionalCardsValues)) > 1 and nonFunctionalCardsValues != set(nonFunctionalCardsValues):
                                pickedCards += [possibleJacks[0]]
                                return pickedCards
                            # else if it is forbidden to put 2 cards
                            elif self.rules['putting_cards'] == 1:
                                # if there are 3 or 4 jacks, put all of them
                                if len(possibleJacks) > 2:
                                    pickedCards += possibleJacks
                                    return pickedCards
                                else:
                                    # if there is 1 or 2 jacks, put only one
                                    pickedCards += [possibleJacks[0]]
                                    return pickedCards
                                    # if it is allowed to put 2 cards, put all of them
                            else:
                                pickedCards += possibleJacks
                                return pickedCards
                        # 1.1.3.2 ace is in possible cards
                        else:
                            if self.rules['putting_cards'] == 1:
                                # if there are 3 or 4 aces, put all of them
                                if len(possibleDemandCards) > 2:
                                    pickedCards += possibleDemandCards
                                    return pickedCards
                                else:
                                    # if there is 1 or 2 aces, put only one
                                    pickedCards += [possibleDemandCards[0]]
                                    return pickedCards
                                    # if it is allowed to put 2 cards, put all of them
                            else:
                                pickedCards += possibleDemandCards
                                return pickedCards
                    #1.1.4 just put anything, as many cards as possible
                    else:
                        potentialSet = []

                        for possibleCard in possibleCards:
                            temp_list = []
                            temp_list += [possibleCard]
                            temp_list += [card for card in self.currentPlayer.hand if
                                          (possibleCard.value == card.value and card != possibleCard)]
                            potentialSet.append(temp_list)

                        maxCardSet = [set for set in potentialSet if
                                      len(set) == max([len(set) for set in potentialSet])]
                        maxCardSet = maxCardSet[0]

                        if self.rules['putting_cards'] == 1:
                            if len(maxCardSet) != 2:
                                pickedCards += maxCardSet
                                return pickedCards
                            else:
                                pickedCards += [maxCardSet[0]]
                                return pickedCards
                        else:
                            # Returns the first biggest possible set (even if it' is 1 card)
                            pickedCards += maxCardSet
                            return pickedCards


                # 1.2 check if computer has more than 6 cards in hand
                elif len(self.currentPlayer.hand) > 6:
                    #1.2.1 check if computer has delay cards
                    if possibleDelayCards:
                        pickedCards += [possibleDelayCards[0]]
                        return pickedCards
                    #1.2.2 check if computer has jacks and what to demand
                    elif nonFunctionalCardsInHand and possibleJacks:
                        pickedCards += [possibleJacks[0]]
                        return pickedCards
                    #1.2.3 just put anything, as many cards as possible
                    else:
                        potentialSet = []

                        for possibleCard in possibleCards:
                            temp_list = []
                            temp_list += [possibleCard]
                            temp_list += [card for card in self.currentPlayer.hand if
                                          (possibleCard.value == card.value and card != possibleCard)]
                            potentialSet.append(temp_list)

                        maxCardSet = [set for set in potentialSet if
                                      len(set) == max([len(set) for set in potentialSet])]
                        maxCardSet = maxCardSet[0]

                        if self.rules['putting_cards'] == 1:
                            if len(maxCardSet) != 2:
                                pickedCards += maxCardSet
                                return pickedCards
                            else:
                                pickedCards += [maxCardSet[0]]
                                return pickedCards
                        else:
                            # Returns the first biggest possible set (even if it' is 1 card)
                            pickedCards += maxCardSet
                            return pickedCards


                # 1.3 else if computer has more than 1 valiant card
                elif len(possibleValiantCards) > 1:
                    pickedCards += [possibleValiantCards[0]]
                    return pickedCards
                # 1.4 else if computer has more than 1 delay card
                elif len(possibleDelayCards) > 1:
                    pickedCards += [possibleDelayCards[0]]
                    return pickedCards


                # 1.5 Check if there is a set
                potentialSet = []

                for possibleCard in possibleCards:
                    temp_list = []
                    temp_list += [possibleCard]
                    temp_list += [card for card in self.currentPlayer.hand if (possibleCard.value == card.value and card != possibleCard)]
                    potentialSet.append(temp_list)

                maxCardSet = [set for set in potentialSet if len(set) == max([len(set) for set in potentialSet])]
                maxCardSet = maxCardSet[0]

                if self.rules['putting_cards'] == 1:
                    if len(maxCardSet) != 2:
                        pickedCards += maxCardSet
                        return pickedCards
                    else:
                        pickedCards += [maxCardSet[0]]
                        return pickedCards
                else:
                    # Returns the first biggest possible set (even if it' is 1 card)
                    pickedCards += maxCardSet
                    return pickedCards

        def put(pickedCards):
            """
            (1) Adds picked cards to the stack, (2) Checks if functional and change state if it is,
            (3) remove picked cards from player.pickedCards [] (4) If it is Jack or Ace set the demand accordingly

            :param pickedCards: list of Card Objects
            :return:
            """
            self.stack.addToStack(pickedCards)
            result = self.isFunctional(pickedCards)
            self.currentPlayer.removeCards()

            if result == "Jack":
                # Finds the most frequently occuring suit in the hand
                nonFunctionalCardsInHand = [card for card in self.currentPlayer.hand if
                                            card.value in range(5,13)]
                if nonFunctionalCardsInHand:
                    valueOccurance = Counter([card.value for card in nonFunctionalCardsInHand])
                    for (key, value) in valueOccurance.items():
                        if value == max(valueOccurance.values()):
                            MostFrequentValue = int(key)
                            break
                    # demand it
                    self.state['type'] = 'jackDemand'
                    self.state['value'] = MostFrequentValue
                    self.state['demandTurns'] = len(self.players) + 1

            elif result == "Ace":
                # demand most frequently occuring suit in the hand
                self.state['type'] = 'aceDemand'
                self.state['value'] = getMostFrequentSuit()

            return

        def moveMostFrequentSuitToEnd():
            """ Modify order of player's pickedCards if it's helpful.
                Looks for the most commontly occuring suit in the hand.
                If suit occurs in picked cards it moves it to the end."""

            # Checks the most frequently occuring suit in the hand
            MostFrequentSuit = getMostFrequentSuit()

            # If one of the picked cards [besides from first card] has the same suit
            cardToMove = [card for card in self.currentPlayer.pickedCards[1:] if card.suit == MostFrequentSuit]
            # Move it to the end of the list
            if cardToMove:
                self.currentPlayer.pickedCards += [self.currentPlayer.pickedCards.pop(self.currentPlayer.pickedCards.index(cardToMove[0]))]

        #Checks if any card matches
        for card in self.currentPlayer.hand:
            result = self.matchWithTopCard([card])
            if not isinstance(result, str):         #means function did not return error
                possibleCards += [card]

        #Checks for Jokers if there's no 'normal matches'
        if not possibleCards:
            for card in self.currentPlayer.hand:
                if card.suit == "Joker":
                    possibleCards += [card]
                    break

        #Take if still nothing
        if not possibleCards:
            #if delay state
            if self.state['type'] == 'delay':
                self.currentPlayer.delay = self.state['value']
                self.resetState()
                return
            #if valiant state
            if self.state['type'] == 'valiant':
                if not self.deck.isSufficient(self.state['value']):
                    self.stack.addToDeck(self.deck)
                self.currentPlayer.takePunishement(self.state['value'], self.deck)
                self.resetState()
                return
            #normal take
            if not self.deck.isSufficient(2):
                self.stack.addToDeck(self.deck)
            newCard = self.currentPlayer.draw(self.deck)

            #if allowed to put new card
            if self.rules["taking_cards"] in [2,3]:
                result = self.matchWithTopCard([newCard])
                #if new card matches
                if not isinstance(result, str):  # means function did not return error
                    self.currentPlayer.hand.remove(newCard)
                    put([newCard])
                    #if more than one card can be added
                    if self.rules["taking_cards"] == 3:
                        matchingCards = [card for card in self.currentPlayer.hand if card.value == newCard.value ]
                        #if any cards matches new card
                        if matchingCards:
                            if self.rules["putting_cards"] == 1:
                                if len(matchingCards) > 1:
                                    #remove cards from hand
                                    for card in matchingCards:
                                        self.currentPlayer.hand.remove(card)
                                    #rearrange order
                                    self.currentPlayer.pickedCards = matchingCards
                                    moveMostFrequentSuitToEnd()
                                    put(matchingCards)
                            else:
                                #remove cards from hand
                                for card in matchingCards:
                                    self.currentPlayer.hand.remove(card)
                                #rearrange order
                                self.currentPlayer.pickedCards = matchingCards
                                moveMostFrequentSuitToEnd()
                                put(matchingCards)
                return
            else:
                return

        #put
        else:
            #pick cards
            self.currentPlayer.pickedCards = think()

            # bug to fix
            # if isinstance(self.currentPlayer.pickedCards[0], list):
            #     self.currentPlayer.pickedCards = self.currentPlayer.pickedCards[0]

            #if comp picked more than 1 card, arrange most useful order
            if len(self.currentPlayer.pickedCards) > 1:
                moveMostFrequentSuitToEnd()
            # remove from hand
            for card in self.currentPlayer.pickedCards:
                self.currentPlayer.hand.remove(card)
            # put
            put(self.currentPlayer.pickedCards)
            return




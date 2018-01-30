from makao.stack import valiantCards, demandCards, delayCards, functionalCards

def deal(players,deck):
        """ Splitting 5 cards to each player """
        for i in range(5):
            for player in players:
                player.draw(deck)

        def resetState(state):
            state = {'type': '', 'value': 0}

#brak turn()
#brak choose()

#brak put() ? - może się udać zuniwersalizować ;) TODO: przyjrzeć się za chwilę


   #UWAGA: TakePunishement przesunięte do Playera
    #UWAGA: sufficentDeck przesunięte do Decka
    # UWAGA: addToDeck przesunięte do Stacka

def matchWithTopCard(pickedCards,stack,state,rules,player):                         # może okazać się nieprzydatne
    """ Checks if picked cards match the top card
        :return boolean """
    result = stack.receive(pickedCards, state, rules)
    if result:
        player.removeCards(pickedCards)
        return True
    else:
        return False


def isFunctional(state, cardList, currentPlayer):                                   #czy funkcja zmieni na stałe state?
    """ Modyfies game state if cards added to the stack are functional               #to musi być "luźno" w views.game()
        :return (dict) state"""
    for card in cardList:
        if card in delayCards:
            state['type'] = 'delay'
            state['value'] += 1
        if card in valiantCards:
            state['type'] = 'valiant'
            if card.value == 13:
                state['value'] += 5
            else:
                state['value'] += card.value
        if card in demandCards:
            if card.value == 1:
                state['type'] = 'aceDemand'
                state['value'] = input("Jakiego koloru żądasz?")
                print(state)
                return state
            elif card.value == 11:
                state['type'] = 'jackDemand'
                state['value'] = int(input("Jakiej karty żądasz?"))
                state['demander'] = currentPlayer
                print(state)
                return state
    return state

#brak take() ? - może się udać zuniwersalizować ;) TODO: przyjrzeć się za chwilę


#takePunishement() moved to Player class

#brak take() ? - może się udać zuniwersalizować ;) TODO: przyjrzeć się za chwilę


def addToWinners(player,winners,players):                                          #TODO: mocno zastanowić się nad tą
        """ Move from players list to winners list"""                               # funkcją; Czy zmieni globalnie?
        winners.append(players.pop(players.index(player)))                          # czy jest potrzebna wyizolowana?

#letUserPickCards będzie zastąpione klikaniem w formularz


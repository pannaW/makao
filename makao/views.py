# encoding=utf8
import pickle
from flask import render_template, session, request, redirect, url_for,flash
from makao import app
from makao.cards import suits, values
from makao.player import Player
from makao.game import Game


def pickle_read(filename):
    pickle_in = open(filename, "rb")
    obj = pickle.load(pickle_in)
    return obj


def pickle_write(filename,obj):
    pickle_out = open(filename, "wb")
    pickle.dump(obj, pickle_out)
    pickle_out.close()


app.secret_key = "super secret key"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/players/', methods=['GET', 'POST'])
def players():
    """ Gets informations about players
    (number of players, players' names) """
    if request.method == 'POST':
        #3. Send data
        session['players_names'] = []
        players_number = int(request.form.get('players_number'))
        for i in range(1,players_number+1):
            session['players_names'].append(request.form.get('player' + str(i) + '-name'))
        return redirect(url_for('players_computers'))
    elif request.method == 'GET':
        #2. Ask about players' names
        if request.args.get('players_number'):
            players_number = int(request.args.get('players_number'))
            return render_template('players.html', players_number=players_number)
        #1. Ask about number of players
    return render_template('players.html')

@app.route('/players/computers')
def players_computers():
    """ Gets information about computer players """
    if len(session.get('players_names')) == 4:
        return redirect(url_for('rules'))
    else:
        if request.args.get('computers_number'):
            session['computers_number'] = request.args.get('computers_number',int)
            return redirect(url_for('rules'))

        return render_template('players_computers.html',players_number=len(session.get('players_names')))


@app.route('/rules', methods=['GET','POST'])
def rules():
    """ Gets informations about rules """
    if request.method == 'POST':
            if request.form.get('end_game') and request.form.get('taking_cards') \
            and request.form.get('putting_cards') and request.form.get('valiant_cards'):

                rules = {'functional_cards': request.form.getlist('functional_cards'),
                         'end_game': int(request.form.get('end_game')),
                         'taking_cards': int(request.form.get('taking_cards')),
                         'putting_cards': int(request.form.get('putting_cards')),
                         'valiant_cards' : int(request.form.get('valiant_cards'))}

                session['rules'] = rules
                return redirect(url_for('begin'))
            else:
                flash('Wypełnij wszystkie pola!')
                return render_template('rules.html')
    return render_template('rules.html')


@app.route('/begin',methods=['GET','POST'])
def begin():
    """ Summary and init """
    if session.get('players_names'):
        # init Players
        players_list = []
        for player in session['players_names']:
            players_list += [Player(player)]

    if session.get('computers_number'):
        for player in range(1,int(session['computers_number'])+1):
            players_list += [Player('Computer ' + str(player), False)]

        # init Game
        game = Game(players_list, session['rules'])

        pickle_write("game.pickle",game)

        session.pop('players_names', None)
        session.pop('rules', None)

        return render_template('begin.html',rules=game.rules,players=game.players)
    else:
        return redirect(url_for('players'))


@app.route('/play',methods=['GET','POST'])
def play():
    game = pickle_read("game.pickle")

    if game.isEnd():
        return redirect(url_for('end_game'))

    game.setCurrentPlayer()
    game.jackDemandEndCondition()
    pickle_write("game.pickle", game)

    if not game.currentPlayer.soul:
        if game.isCurrentPlayerSkipping():
            pickle_write("game.pickle", game)
        else:
            game.computerStrategy()
            pickle_write("game.pickle", game)
        return redirect(url_for('next_player'))


    if game.isCurrentPlayerSkipping():
        pickle_write("game.pickle", game)
        return render_template('player_delayed.html',competitors=game.showCompetitors(), game=game, player=game.currentPlayer,
                           picked_cards=game.currentPlayer.pickedCards,topCard=game.stack.getTopCard(), values=values)
    else:
        if not game.currentPlayer.soul:
            game.computerStrategy()
            pickle_write("game.pickle", game)
            return redirect(url_for('next_player'))
        else:
            return redirect(url_for('pick_cards'))


@app.route('/pick_cards', methods=['GET','POST'])
def pick_cards():
    """ Lets player picks cards one by one """
    game = pickle_read("game.pickle")
    session.pop('joker_index', None)

    if request.args.get("end"):
        return redirect(url_for('validation_1'))

    if request.args.get("value"):
        card_index = request.args.get("value",type=int)
        #if not RENAMED joker
        if game.currentPlayer.hand[card_index].value == 0:
            session['joker_index'] = int(card_index)
            return redirect(url_for('rename_joker'))
        else:
            game.currentPlayer.pickCard(card_index)
            pickle_write("game.pickle",game)

    return render_template('pick_cards.html',competitors=game.showCompetitors(), game=game, player=game.currentPlayer,
                           picked_cards=game.currentPlayer.pickedCards,topCard=game.stack.getTopCard(), values=values)


@app.route('/joker')
def rename_joker():
    """ Lets user rename joker """
    game = pickle_read("game.pickle")

    if request.args.get('suit') and request.args.get('value'):
        suit = request.args.get('suit',type=str)
        value = request.args.get('value',type=int)
        game.currentPlayer.hand[session['joker_index']].renameJoker(suit,value)
        pickle_write("game.pickle", game)
        session.pop('joker_index', None)
        return redirect(url_for('pick_cards'))

    return render_template('joker.html',competitors=game.showCompetitors(), game=game, player=game.currentPlayer,
                           picked_cards=game.currentPlayer.pickedCards,topCard=game.stack.getTopCard(),values=values,
                            suits=suits)


@app.route('/validation_1')
def validation_1():
    """Checks if (1) cards were picked, (2) correct amount of cards were picked (3) all cards have the same value"""
    game = pickle_read("game.pickle")
    result = game.checkPickedCards(game.currentPlayer.pickedCards)

    if isinstance(result,str):                  #error
        game.resetJokers(game.currentPlayer.pickedCards)
        game.currentPlayer.cancelPickedCards()
        pickle_write("game.pickle", game)
        flash(result)

        if session.get('takeProcessFlag'):
            session.pop('takeProcessFlag',None)
            return redirect(url_for('next_player'))
        else:
            return redirect(url_for('play'))
    else:
        return redirect(url_for('validation_2'))


@app.route('/validation_2')
def validation_2():
    """Checks if (1) cards match top card (2) if cards are functional."""
    game = pickle_read("game.pickle")
    result = game.matchWithTopCard(game.currentPlayer.pickedCards)

    if isinstance(result,str):                  #error
        game.resetJokers(game.currentPlayer.pickedCards)
        game.currentPlayer.cancelPickedCards()
        pickle_write("game.pickle", game)
        flash(result)
        if session.get('takeProcessFlag'):
            session.pop('takeProcessFlag', None)
            return redirect(url_for('next_player'))
        else:
            return redirect(url_for('play'))
    else:
        game.stack.addToStack(game.currentPlayer.pickedCards)
        result = game.isFunctional(game.currentPlayer.pickedCards)
        game.currentPlayer.removeCards()

        if result == "Ace" or result == "Jack":
            session['demand'] = result

            pickle_write("game.pickle", game)
            return redirect(url_for('demand'))
        else:
            pickle_write("game.pickle", game)
            return redirect(url_for('next_player'))


@app.route('/demand')
def demand():
    """Lets player pick demanded suit or value """
    game = pickle_read("game.pickle")
    if session.get('demand') == "Ace":
        # 2. Interpretuj wybór
        if request.args.get('suit'):
            # 2a. Jeśli niczego nie żąda
            if request.args.get('suit') == "no":
                session.pop('demand', None)
                return redirect(url_for('next_player'))
            #2b. Jeśli żąda
            else:
                game.state['type'] = 'aceDemand'
                game.state['value'] = request.args.get('suit',type=str)
                pickle_write("game.pickle", game)
                session.pop('demand', None)
                return redirect(url_for('next_player'))
        #1. Wyrenderuj formularz
        return render_template('ace_demand.html',competitors=game.showCompetitors(), game=game, player=game.currentPlayer,
                               picked_cards=game.currentPlayer.pickedCards,topCard=game.stack.getTopCard(),
                               values=values,suits=suits)

    elif session['demand'] == "Jack":
        game = pickle_read("game.pickle")
        #2. Intepretuj wybór
        if request.args.get('value'):
            session.pop('demand', None)
            # 2a. Jeśli niczego nie żąda
            if request.args.get('value') == "no":
                session.pop('demand', None)
                return redirect(url_for('next_player'))
            # 2b. Jeśli żąda
            else:
                game = pickle_read("game.pickle")
                game.state['type'] = 'jackDemand'
                game.state['value'] = request.args.get('value',type=int)
                game.state['demandTurns'] = len(game.players) + 1
                session.pop('demand', None)
                pickle_write("game.pickle", game)
                return redirect(url_for('next_player'))
        #1. Wyrenderuj formularz
        return render_template('jack_demand.html',competitors=game.showCompetitors(), game=game, player=game.currentPlayer,
                           picked_cards=game.currentPlayer.pickedCards,topCard=game.stack.getTopCard(), values=values)


@app.route('/take')
def take():
    """ Modyfications after player chooses to take """
    game = pickle_read("game.pickle")

    if request.args.get("answer"):
        if request.args.get("answer", type=str) == "no":
            return redirect(url_for('next_player'))
        elif request.args.get("answer", type=str) == "yes":
            game.currentPlayer.pickCard(-1)
            session['takeProcessFlag'] = True
            pickle_write("game.pickle", game)
            if game.currentPlayer.pickedCards[0].joker:
                return redirect(url_for('take_rename_joker'))

            else:
                if game.rules["taking_cards"] == 2:
                    return redirect(url_for('validation_2'))
                else:
                    return redirect(url_for('pick_cards'))

    if game.state['type'] == 'delay':
        game.currentPlayer.delay = game.state['value']
        game.resetState()
        pickle_write("game.pickle", game)
        return render_template('take_delay.html',competitors=game.showCompetitors(), game=game, player=game.currentPlayer,
                          topCard=game.stack.getTopCard(), values=values)

    if game.state['type'] == 'valiant':
        if not game.deck.isSufficient(game.state['value']):
            game.stack.addToDeck(game.deck)
        newCards = []
        newCards.extend(game.currentPlayer.takePunishement(game.state['value'], game.deck))
        game.resetState()
        pickle_write("game.pickle", game)
        return render_template('take_punishement.html', competitors=game.showCompetitors(), game=game,
                               player=game.currentPlayer,topCard=game.stack.getTopCard(), values=values,new_cards=newCards)
    else:
        if not game.deck.isSufficient(2):
            game.stack.addToDeck(game.deck)

        newCard = game.currentPlayer.draw(game.deck)
        pickle_write("game.pickle", game)

        return render_template('take.html',game=game, player=game.currentPlayer,competitors=game.showCompetitors(),
                               topCard=game.stack.getTopCard(), rules=game.rules,values=values, new_card=newCard)


@app.route('/take/joker')
def take_rename_joker():
    """ Let the user rename joker that he has just draw, in order to put it on the stack """
    game = pickle_read("game.pickle")

    if request.args.get('suit') and request.args.get('value'):
        suit = request.args.get('suit', type=str)
        value = request.args.get('value', type=int)
        game.currentPlayer.pickedCards[0].renameJoker(suit, value)
        pickle_write("game.pickle", game)
        session.pop('joker_index', None)
        if game.rules["taking_cards"] == 2:
            return redirect(url_for('validation_2'))
        else:
            return redirect(url_for('pick_cards'))

    return render_template('joker.html',competitors=game.showCompetitors(), game=game, player=game.currentPlayer,
                           picked_cards=game.currentPlayer.pickedCards,topCard=game.stack.getTopCard(), values=values,
                           suits=suits, take=True)


@app.route('/next-player')
def next_player():
    """ Modyfications to process player forwardng """
    session.pop('takeProcessFlag', None)
    session.pop('joker_index', None)

    game = pickle_read("game.pickle")
    game.nextPlayer()
    pickle_write("game.pickle",game)
    return redirect(url_for('play'))


@app.route('/end')
def end_game():
    """ Displays winner"""
    game = pickle_read("game.pickle")
    return render_template('end_game.html', winners=game.winners)


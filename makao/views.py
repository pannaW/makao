# encoding=utf8
import pickle
from flask import render_template, session, request, redirect, url_for,flash
from makao import app
from makao.cards import suits, values
from makao.player import Player
from makao.gameObject import Game


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
        return redirect(url_for('rules'))
    elif request.method == 'GET':
        #2. Ask about players' names
        if request.args.get('players_number'):
            players_number = int(request.args.get('players_number'))
            return render_template('players.html', players_number=players_number)
        #1. Ask about number of players
    return render_template('players.html')


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
               #init rules
                session['rules'] = rules
                return redirect(url_for('begin'))
            else:
                flash('Wypełnij wszystkie pola!')
                return render_template('rules.html')
    return render_template('rules.html')


@app.route('/begin',methods=['GET','POST'])
def begin():
    """ Summary and init """

    # init Players
    players_list = []
    for player in session['players_names']:
        players_list += [Player(player)]
    # init Game
    game = Game(players_list, session['rules'])

    pickle_write("game.pickle",game)

    session.pop('players_names', None)
    session.pop('rules', None)

    return render_template('begin.html',rules=game.rules,players=game.players)


@app.route('/play',methods=['GET','POST'])
def play():
    game = pickle_read("game.pickle")

    if game.isEnd():
        return redirect(url_for('end_game'))

    game.setCurrentPlayer()
    game.jackDemandEndCondition()
    pickle_write("game.pickle", game)

    if game.isCurrentPlayerSkipping():
        pickle_write("game.pickle", game)
        return render_template('player_delayed.html', player=game.currentPlayer)
    else:
        return render_template('play.html', game=game, player=game.currentPlayer, competitors=game.showCompetitors(),
                               topCard=game.stack.getTopCard(), values=values)


@app.route('/pick_cards', methods=['GET','POST'])
def pick_cards():
    """ Let player picks cards one by one """
    game = pickle_read("game.pickle")
    session.pop('joker_index', None)

    if request.args.get("end"):
        return redirect(url_for('validation_1'))

    if request.args.get("value"):
        card_index = request.args.get("value",type=int)
        #if NOT RENAMED Joker
        if game.currentPlayer.hand[card_index].value == 0:
            session['joker_index'] = int(card_index)
            return redirect(url_for('rename_joker'))
        else:
            game.currentPlayer.pickCard(card_index)
            pickle_write("game.pickle",game)

    return render_template('pick_cards.html',game=game, player=game.currentPlayer,
                           pickedCards=game.currentPlayer.pickedCards,topCard=game.stack.getTopCard(), values=values)


@app.route('/joker')
def rename_joker():
    game = pickle_read("game.pickle")

    if request.args.get('suit') and request.args.get('value'):
        suit = request.args.get('suit',type=str)
        value = request.args.get('value',type=int)
        game.currentPlayer.hand[session['joker_index']].renameJoker(suit,value)
        pickle_write("game.pickle", game)
        session.pop('joker_index', None)
        return redirect(url_for('pick_cards'))

    return render_template('joker.html',game=game, player=game.currentPlayer,topCard=game.stack.getTopCard(),
                           values=values,suits=suits)


@app.route('/validation_1')
def validation_1():
    """
    Checks if (1) cards were picked, (2) correct amount of cards were picked (3) all cards have the same value
    :return: redirect
    """
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
        return render_template('ace_demand.html',game=game, player=game.currentPlayer,
                           pickedCards=game.currentPlayer.pickedCards,topCard=game.stack.getTopCard(),suits=suits)

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
        return render_template('jack_demand.html',game=game, player=game.currentPlayer,
                           pickedCards=game.currentPlayer.pickedCards,topCard=game.stack.getTopCard())


@app.route('/take')
def take():
    game = pickle_read("game.pickle")

    if request.args.get("answer"):
        if request.args.get("answer", type=str) == "no":
            return redirect(url_for('next_player'))
        elif request.args.get("answer", type=str) == "yes":
            game.currentPlayer.pickCard(-1)
            session['takeProcessFlag'] = True
            pickle_write("game.pickle", game)
            if game.currentPlayer.pickedCards[0].joker:         #tego się nie da też jakoś podciągnąć pod normalnego jokera?
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
        return render_template('take_delay.html',player=game.currentPlayer)

    if game.state['type'] == 'valiant':
        if not game.deck.isSufficient(game.state['value']):
            game.stack.addToDeck(game.deck)
        game.currentPlayer.takePunishement(game.state['value'], game.deck)
        game.resetState()
        pickle_write("game.pickle", game)
        return render_template('take_punishement.html', player=game.currentPlayer)
    else:
        if not game.deck.isSufficient(2):
            game.stack.addToDeck(game.deck)

        game.currentPlayer.draw(game.deck)
        pickle_write("game.pickle", game)

        return render_template('take.html',game=game, player=game.currentPlayer,competitors=game.showCompetitors(),
                               topCard=game.stack.getTopCard(), rules=game.rules)


@app.route('/take/joker')
def take_rename_joker():
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

    return render_template('joker.html',topCard=game.stack.getTopCard(), game=game, player=game.currentPlayer,
                            values=values, suits=suits, take=True)


@app.route('/next-player')
def next_player():
    session.pop('takeProcessFlag', None)
    game = pickle_read("game.pickle")
    game.nextPlayer()
    pickle_write("game.pickle",game)
    return redirect(url_for('play'))


@app.route('/end')
def end_game():
    game = pickle_read("game.pickle")
    return render_template('end_game.html', winners=game.winners)


# @app.route('/game/player/next')         #jaką to ma funkcję
# def game_next():
# @app.context_processor
# def inject_variables():
#     return dict(
#         user={'name': 'Alicja'},
#         posts=[
#             {
#                 'post_id': 0,
#                 'title': 'Post numer 1'
#             },
#             {
#                 'post_id': 1,
#                 'title': 'Post numer 2'
#             },
#             {
#                 'post_id': 2,
#                 'title': 'Post numer 3'
#             }]
#         )

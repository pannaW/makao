# encoding=utf8
from flask import render_template, session, request, redirect, url_for,flash
from makao import app
from makao.player import Player
from makao.gameObject import Game


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
                rules = dict()
                rules['functional_cards'] = list()
                if request.form.get('queen'):
                    rules['functional_cards'] += ['queen']
                if request.form.get('joker'):
                    rules['functional_cards'] += ['joker']
                rules['end_game'] = int(request.form.get('end_game'))
                rules['taking_cards'] = int(request.form.get('taking_cards'))
                rules['putting_cards'] = int(request.form.get('putting_cards'))
                rules['valiant_cards'] = int(request.form.get('valiant_cards'))
                #init rules
                session['rules'] = rules
                return redirect(url_for('begin'))
            else:
                flash('Wypełnij wszystkie pola!')
                return render_template('rules.html')
    return render_template('rules.html')


@app.route('/begin',methods=['GET','POST'])
def begin():
    """ Summary and init of everything """
    return render_template('begin.html',rules=session['rules'],players_names=session['players_names'])


@app.route('/game',methods=['GET','POST'])
def game():
    #init players
    players_list = []
    for player in session['players_names']:
        players_list += [Player(player)]
    #init game
    game = Game(players_list,session['rules'])

    while not game.isEnd():
        game.turn(game.players[game.currentPlayerId])
        # ...


        game.currentPlayerId += 1

        if game.currentPlayerId == len(game.players):
            game.currentPlayerId = 0

    for winner in game.winners:
        session['winners_names'] += winner.name
    return redirect(url_for('end_game'))

@app.route('/end')
def end_game():
    return render_template('end_game.html', winners_names=session['winners_names'])


#====================================================================================================

# @app.route('/game/player/')             #<int:id> ?
# def game():
#     """ogólne warunki końca gry itd.
# render: currentPlayer (with his cards and all), stack (top card), stan gry
# (turn) o ile nie stoi kolejki
#     #(choose)wybór akcji: take lub put
#         #(letUserPickCards) czyli niech wybiera sobie karty które chce wyrzucić
#         #(put) czyli sprawdzamy czy pasują do siebie
# """



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

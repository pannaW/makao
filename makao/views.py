# encoding=utf8
from flask import render_template, session, request
from makao import app

app.secret_key = "super secret key"

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/begin',methods=['GET','POST'])
def begin():
    session['functional_cards'] = list()
    if request.form.get('queen'):
        session['functional_cards'].append('queen')
    if request.form.get('joker'):
        session['functional_cards'].append('joker')
    if request.form.get('end_game'):
        value = request.form.get('end_game')
        session['end_game'] = int(value)
    if request.form.get('taking_cards'):
        value = request.form.get('taking_cards')
        session['taking_cards'] = int(value)
    if request.form.get('putting_cards'):
        value = request.form.get('putting_cards')
        session['putting_cards'] = int(value)
    if request.form.get('valiant_cards'):
        value = request.form.get('valiant_cards')
        session['valiant_cards'] = int(value)
    return render_template('begin.html', functional_cards =  session['functional_cards'],end_game = session['end_game'],
    taking_cards = session['taking_cards'], putting_cards = session['putting_cards'],
                           valiant_cards = session['valiant_cards'])


@app.route('/rules',methods=['GET','POST'])
def rules():
    return render_template('rules.html')

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

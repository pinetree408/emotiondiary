from flask import Flask, g, render_template, redirect, url_for, session, request
from flask_oauth import OAuth
from flask_sqlalchemy import SQLAlchemy
from os import path
from datetime import datetime, date, time

import sqlite3
import json

SECRET_KEY = 'development key'
DEBUG = True
FACEBOOK_APP_ID = ''
FACEBOOK_APP_SECRET = ''

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

BASE_DIRECTORY = path.abspath(path.dirname(__file__))
dbURL = '{0}{1}'.format('sqlite:///', path.join(BASE_DIRECTORY, 'app.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = dbURL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class Calendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emotion = db.Column(db.Integer)
    content = db.Column(db.Text)
    pub_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def as_dict(self):
        data = {
            'id': self.id,
            'created_at': self.pub_date.strftime('%Y-%m-%d'),
            'text': self.content,
            'emotion': self.emotion
        }
        return json.dumps(data)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facebookID = db.Column(db.Unicode, unique=True)
    name = db.Column(db.Unicode)

db.create_all()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret=FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email'}
)

@app.route("/")
def index():
    if session.get('user'):
        user = session.get('user')
        return render_template('index.html', user = user)
    return redirect(url_for('login'))

@app.route("/calendar")
def calendar():
    user = session.get('user')
    today = datetime.combine(date.today(), time(0,0,0))
    calendar = Calendar.query.filter_by(user_id=user['id'], pub_date=today).first()
    if not calendar:
        return redirect(url_for('calendar_create'))
    calendar_objects = Calendar.query.filter_by(user_id=user['id']).all()
    calendar_list = list(map(lambda c_object: c_object.as_dict(), calendar_objects))
    return render_template('calendar/index.html', calendar_list=calendar_list)

@app.route("/calendar/create", methods=['GET', 'POST'])
def calendar_create():
    user = session.get('user')
    if request.method == 'POST':
        emotion = request.form['optionsRadios']
        message = request.form['message']
        today = datetime.combine(date.today(), time(0,0,0))
        calendar = Calendar(content=str(message), emotion=int(emotion), pub_date=today, user_id=user['id'])
        db.session.add(calendar)
        db.session.commit()
        return redirect(url_for('calendar'))
    return render_template('calendar/create.html')

@app.route("/calendar/emotion/<int:id>", methods=['GET', 'POST'])
def calendar_emotion(id):
    user = session.get('user')
    calendar = Calendar.query.filter_by(id=id).first()
    calendar_info = calendar.as_dict()
    return render_template('calendar/detail.html', calendar_info=calendar_info)

@app.route("/tips")
def tips():
    tipFile = open('static/txt/tips.txt', 'r')
    tipLines = tipFile.readlines()

    result = []
    for tipLine in tipLines:
        splittedTip = tipLine.split('    ')
        print splittedTip
        if len(splittedTip) == 1:
            continue
        tipDict = {}
        tipDict['number'] = splittedTip[0]
        tipDict['locale'] = splittedTip[1]
        tipDict['tip'] = splittedTip[2]
        tipDict['cite'] = splittedTip[3]
        tipDict['url'] = splittedTip[4]
        tipDict['quotation'] = splittedTip[5]
        tipDict['question'] = splittedTip[6]
        tipDict['answer'] = splittedTip[7]
        #tipDict['wrong'] = splittedTip[8]
        result.append(tipDict)
    return render_template('tips.html', tips=result)


@app.route('/login')
def login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    # For test
    if session.get('user'):
        return redirect(url_for('index'))
    user = User.query.filter_by(facebookID=me.data['id']).first()
    if not user:
        user = User(facebookID=str(me.data['id']), name=me.data['name'])
        db.session.add(user)
        session['user'] = dict(id=user.id, name=user.name, facebookID=user.facebookID)
    db.session.commit()
    return redirect(url_for('index'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


if __name__ == "__main__":
    app.run()

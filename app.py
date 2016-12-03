from flask import Flask, g, render_template, redirect, url_for, session, request
from flask_oauth import OAuth
from flask_sqlalchemy import SQLAlchemy
from os import path

import sqlite3

SECRET_KEY = 'development key'
DEBUG = True
FACEBOOK_APP_ID = '1829475553997900'
FACEBOOK_APP_SECRET = '1e4e5d260836e4bc156ee5f8d573b743'

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

BASE_DIRECTORY = path.abspath(path.dirname(__file__))
dbURL = '{0}{1}'.format('sqlite:///', path.join(BASE_DIRECTORY, 'app.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = dbURL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
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
    return render_template('calendar.html')

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
        session['user'] = dict(name=user.name, facebookID=user.facebookID)
    db.session.commit()
    return redirect(url_for('index'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')


if __name__ == "__main__":
    app.run()

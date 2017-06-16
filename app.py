import json
import random
from os import path
from datetime import datetime, date, time
import facebook_info

from flask import Flask, render_template, redirect, url_for, session, request
from flask_oauth import OAuth
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext import mutable

SECRET_KEY = 'development key'
DEBUG = True
FACEBOOK_APP_ID = facebook_info.APP_ID
FACEBOOK_APP_SECRET = facebook_info.APP_SECRET

app = Flask(__name__)
app.debug = DEBUG
app.secret_key = SECRET_KEY
oauth = OAuth()

BASE_DIRECTORY = path.abspath(path.dirname(__file__))
DB_URL = '{0}{1}'.format('sqlite:///', path.join(BASE_DIRECTORY, 'emotiondiary.db'))
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)

class JsonEncodedDict(db.TypeDecorator):
    """Enables JSON storage by encoding and decoding on the fly."""
    impl = db.Text

    def process_bind_param(self, value):
        if value is None:
            return '{}'
        return json.dumps(value)

    def process_result_value(self, value):
        if value is None:
            return {}
        return json.loads(value)

mutable.MutableDict.associate_with(JsonEncodedDict)

class Calendar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    emotion = db.Column(db.Integer)
    degree = db.Column(db.Integer)
    content = db.Column(JsonEncodedDict)
    pub_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def as_dict(self):
        data = {
            'id': self.id,
            'created_at': self.pub_date.strftime('%Y-%m-%d'),
            'text': self.content,
            'emotion': self.emotion,
            'degree': self.degree
        }
        return json.dumps(data)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    facebookID = db.Column(db.Unicode, unique=True)
    name = db.Column(db.Unicode)

class Tip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    locale = db.Column(db.String(2))
    tip = db.Column(db.Text)
    cite = db.Column(db.Text)
    url = db.Column(db.Text)
    quotation = db.Column(db.Text)
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    choices = db.Column(db.PickleType)

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Text)
    result = db.Column(db.Integer)
    pub_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    result = db.Column(db.Integer)
    pub_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

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

def tip_builder():
    tip_file = open('static/txt/tips.txt', 'r')
    tip_lines = tip_file.readlines()

    for tip_line in tip_lines:
        splitted_tip = tip_line.split('\t')
        if len(splitted_tip) == 1:
            continue
        choices = []
        for item in splitted_tip[7:]:
            if item.strip():
                choices.append(item.strip().decode('utf-8'))

        tip_object = Tip(number=splitted_tip[0].strip(),
                         locale=splitted_tip[1].strip(),
                         tip=splitted_tip[2].strip().decode('utf-8'),
                         cite=splitted_tip[3].strip(),
                         url=splitted_tip[4].strip(),
                         quotation=splitted_tip[5].strip().decode('utf-8'),
                         question=splitted_tip[6].strip().decode('utf-8'),
                         answer=splitted_tip[7].strip().decode('utf-8'),
                         choices=choices
                        )
        db.session.add(tip_object)
        db.session.commit()

tip_builder()

@app.route("/")
def index():
    if session.get('user'):
        user = session.get('user')
        return render_template('index.html', user=user)
    return redirect(url_for('login'))

@app.route("/calendar")
def calendar():
    user = session.get('user')
    today = datetime.combine(date.today(), time(0, 0, 0))
    calendar_info = Calendar.query.filter_by(user_id=user['id'], pub_date=today).first()
    if not calendar_info:
        return redirect(url_for('calendar_create'))
    calendar_objects = Calendar.query.filter_by(user_id=user['id']).all()
    calendar_list = list(map(lambda c_object: c_object.as_dict(), calendar_objects))
    return render_template('calendar/index.html', calendar_list=calendar_list)

@app.route("/calendar/create", methods=['GET', 'POST'])
def calendar_create():
    user = session.get('user')
    if request.method == 'POST':
        json_data = request.get_json()
        emotion = int(json_data['emotion'])
        degree = int(json_data['degree'])
        message = json_data['message']
        today = datetime.combine(date.today(), time(0, 0, 0))
        calendar_item = Calendar(content=message,
                                 emotion=emotion,
                                 degree=degree,
                                 pub_date=today,
                                 user_id=user['id'])
        db.session.add(calendar_item)
        db.session.commit()
        return (json.dumps({'success':True, 'redirect': '/calendar'}),
                200,
                {'ContentType':'application/json'})
    emotion_contents = [
        ("Very Bad", "img/calendar/emotion-2.png"),
        ("Bad", "img/calendar/emotion-1.png"),
        ("So So", "img/calendar/emotion0.png"),
        ("Good", "img/calendar/emotion1.png"),
        ("Very Good", "img/calendar/emotion2.png")
    ]
    emotion_degrees = [
        ("Very Weakly", "img/calendar/degree1.png"),
        ("Weakly", "img/calendar/degree2.png"),
        ("So So", "img/calendar/degree3.png"),
        ("Strong", "img/calendar/degree4.png"),
        ("Very Strong", "img/calendar/degree5.png")
    ]
    message = [
        "Write down today's or past major events and events \
                that have had the greatest impact on your mood today.",
        "Please feel free to write your feelings about the above events, work or thoughts.",
        "You wrote about today's events, work and feelings. \
                If you have words of praise, encouragement, understanding, enlightenment \
                that you can give to yourself in this regard, please write it freely."
    ]
    return render_template('calendar/create/index.html',
                           emotion_contents=emotion_contents,
                           emotion_degrees=emotion_degrees,
                           message=message
                          )

@app.route("/calendar/emotion/<int:calendar_id>", methods=['GET', 'POST'])
def calendar_emotion(calendar_id):
    calendar_item = Calendar.query.filter_by(id=calendar_id).first()
    calendar_info = json.loads(calendar_item.as_dict())
    return render_template('calendar/detail.html', calendar_info=calendar_info)

@app.route("/tips", methods=['GET', 'POST'])
def tips():
    if request.method == 'POST':
        answer = request.form['optionsRadios']
        number = request.form['tip_number']
        locale = request.form['tip_locale']
        tip = Tip.query.filter_by(number=int(number), locale=locale).first()
        if tip.answer == answer:
            return render_template('tip/correct.html')
        return render_template('tip/wrong.html')
    tip = Tip.query.filter_by(locale='KR', number=random.randint(1, 10)).first()
    return render_template('tip/index.html', tips=tip)

@app.route("/tests", methods=["GET", "POST"])
def tests():
    user = session.get('user')
    if request.method == "POST":
        score = []
        for i in range(20):
            score_item = eval("request.form.get('var" + str(i) + "')")
            if score_item:
                score.append(int(score_item))
        scoresum = int(sum(score))
        today = datetime.combine(date.today(), time(0, 0, 0))
        test_item = Test(category="ces-d", result=scoresum, pub_date=today, user_id=user['id'])
        db.session.add(test_item)
        db.session.commit()
        if scoresum < 10:
            return render_template("tests/feedback1.html", user_name=user['name'])
        elif 10 <= scoresum < 21:
            return render_template("tests/feedback2.html", user_name=user['name'])
        return render_template("tests/feedback3.html", user_name=user['name'])
    return render_template("tests/ces-d.html")

@app.route("/game", methods=["GET", "POST"])
def game():
    user = session.get('user')
    if request.method == 'POST':
        result = request.form['result']
        today = datetime.combine(date.today(), time(0, 0, 0))
        game_item = Game(result=int(result), pub_date=today, user_id=user['id'])
        db.session.add(game_item)
        db.session.commit()
        return redirect(url_for('game'))
    return render_template("game/stroop.html")

@app.route("/game/instruction")
def game_instruction():
    return render_template("game/instructions.html")

@app.route("/about")
def about():
    return render_template("about/index.html")

@app.route('/login')
def login():
    return facebook.authorize(
        callback=url_for('facebook_authorized',
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
    me_info = facebook.get('/me')
    # For test
    if session.get('user'):
        return redirect(url_for('index'))
    user = User.query.filter_by(facebookID=me_info.data['id']).first()
    if not user:
        user = User(facebookID=str(me_info.data['id']), name=me_info.data['name'])
        db.session.add(user)
        session['user'] = dict(id=user.id, name=user.name, facebookID=user.facebookID)
    db.session.commit()
    return redirect(url_for('index'))

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

if __name__ == "__main__":
    app.run()

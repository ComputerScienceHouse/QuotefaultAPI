import json
import os
import random
from datetime import datetime

import binascii
import requests
from flask import Flask, request, jsonify, session
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

if os.path.exists(os.path.join(os.getcwd(), "config.py")):
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
else:
    app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))
db = SQLAlchemy(app)

# Disable SSL certificate verification warning
requests.packages.urllib3.disable_warnings()

# Disable SQLAlchemy modification tracking
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
auth = OIDCAuthentication(app,
                          issuer=app.config['OIDC_ISSUER'],
                          client_registration_info=app.config['OIDC_CLIENT_CONFIG'])

app.secret_key = 'submission'  # allows message flashing, var not actually used


# create the quote table with all relevant columns
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    submitter = db.Column(db.String(80))
    quote = db.Column(db.String(200), unique=True)
    speaker = db.Column(db.String(50))
    quoteTime = db.Column(db.DateTime)

    # initialize a row for the Quote table
    def __init__(self, submitter, quote, speaker):
        self.quoteTime = datetime.now()
        self.submitter = submitter
        self.quote = quote
        self.speaker = speaker


class APIKey(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(64), unique=True)
    owner = db.Column(db.String(80))

    def __init__(self, owner):
        self.hash = binascii.b2a_hex(os.urandom(10))
        self.owner = owner


@app.route('/between/<start>/<limit>', methods=['GET'])
def between(start, limit):
    if datetime.strptime(start, "%Y-%m-%d") < datetime.strptime(limit, "%Y-%m-%d"):
        quotes = Quote.query.filter(Quote.quoteTime.between(start, limit)).all()
        return jsonify(parse_as_json(quotes))
    quotes = Quote.query.all
    return jsonify(parse_as_json(quotes))


@app.route('/create', methods=['PUT'])
def create_quote():
    data = json.loads(request.data.decode('utf-8'))

    if data['quote'] and data['submitter'] and data['speaker']:
        quote = data['quote']
        submitter = data['submitter']
        speaker = data['speaker']

        if Quote.query.filter(Quote.quote == quote).first() is not None:
            return "that quote has already been said, asshole"
        elif quote is '' or speaker is '':
            return "you didn't fill in one of your fields. You literally only had two responsibilities, and somehow" \
                   "you fucked them up."
        else:
            new_quote = Quote(submitter=submitter, quote=quote, speaker=speaker)
            db.session.add(new_quote)
            db.session.flush()
            db.session.commit()


@app.route('/all', methods=['GET'])
def index():
    db.create_all()

    date = request.args.get('date')
    submitter = request.args.get('submitter')

    if date is not None and submitter is not None:
        quotes = Quote.query.filter_by(quoteTime=date, submitter=submitter).all()
        return jsonify(parse_as_json(quotes))

    elif date is not None:
        quotes = Quote.query.filter_by(quoteTime=date).all()
        return jsonify(parse_as_json(quotes))

    elif submitter is not None:
        quotes = Quote.query.filter_by(submitter=submitter)
        return jsonify(parse_as_json(quotes))

    quotes = Quote.query.all()  # collect all quote rows in the Quote db
    return jsonify(parse_as_json(quotes))


@app.route('/random', methods=['GET'])
def random_quote():
    date = request.args.get('date')
    submitter = request.args.get('submitter')

    if date is not None and submitter is not None:
        quotes = Quote.query.filter_by(quoteTime=date, submitter=submitter).all()
        random_index = random.randint(0, len(quotes))
        return jsonify(return_json(quotes[random_index]))

    elif date is not None:
        quotes = Quote.query.filter_by(quoteTime=date).all()
        random_index = random.randint(0, len(quotes))
        return jsonify(return_json(quotes[random_index]))

    elif submitter is not None:
        quotes = Quote.query.filter_by(submitter=submitter).all()
        random_index = random.randint(0, len(quotes))
        return jsonify(return_json(quotes[random_index]))

    quotes = Quote.query.all()
    random_index = random.randint(0, len(quotes))
    return jsonify(return_json(quotes[random_index]))


@app.route('/newest', methods=['GET'])
def newest():
    date = request.args.get('date')
    submitter = request.args.get('submitter')

    if date is not None:
        return jsonify(return_json(Quote.query.order_by(Quote.id.desc()).filter_by(date=date).first()))

    elif submitter is not None:
        return jsonify(return_json(Quote.query.order_by(Quote.id.desc()).filter_by(submitter=submitter).first()))

    return jsonify(return_json(Quote.query.order_by(Quote.id.desc()).first()))


@auth.oidc_auth
@app.route('/generatekey')
def generate_API_key():
    new_key = APIKey(str(session["userinfo"].get("preferred_username", "")))
    db.session.add(new_key)
    db.session.flush()
    db.session.commit()
    return new_key.hash


def return_json(quote):
    return {quote.id: {
        'quote': quote.quote,
        'submitter': quote.submitter,
        'speaker': quote.speaker,
        'quoteTime': quote.quoteTime,
    }}


def parse_as_json(quotes, quote_json=None):
    if quote_json is None:
        quote_json = []
    for quote in quotes:
        quote_json.append(return_json(quote))
    return quote_json

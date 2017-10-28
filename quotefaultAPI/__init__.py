import binascii
import json
import os
import random
from datetime import datetime

import markdown as markdown
import requests
from flask import Flask, request, jsonify, session
from flask_pyoidc.flask_pyoidc import OIDCAuthentication
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint

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
    reason = db.Column(db.String(120))
    __table_args__ = (UniqueConstraint('owner', 'reason', name='unique_key'),)

    def __init__(self, owner, reason):
        self.hash = binascii.b2a_hex(os.urandom(10))
        self.owner = owner
        self.reason = reason


@app.route('/', methods=['GET'])
def index():
    db.create_all()
    f = open('README.md', 'r')
    return markdown.markdown(f.read())


@app.route('/<api_key>/between/<start>/<limit>', methods=['GET'])
def between(start, limit, api_key):
    if check_key(api_key):
        if datetime.strptime(start, "%Y-%m-%d") < datetime.strptime(limit, "%Y-%m-%d"):
            quotes = Quote.query.filter(Quote.quoteTime.between(start, limit)).all()
            return jsonify(parse_as_json(quotes))
        quotes = Quote.query.all
        return jsonify(parse_as_json(quotes))
    else:
        return "Invalid API Key!"


@app.route('/<api_key>/create', methods=['PUT'])
def create_quote(api_key):
    if check_key(api_key):
        data = json.loads(request.data.decode('utf-8'))

        if data['quote'] and data['speaker']:
            quote = data['quote']
            submitter = APIKey.query.filter_by(hash=api_key).all()[0].owner
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
                return return_json(new_quote)
    else:
        return "Invalid API Key!"


@app.route('/<api_key>/all', methods=['GET'])
def all_quotes(api_key):
    if check_key(api_key):
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
    else:
        return "Invalid API Key!"


@app.route('/<api_key>/random', methods=['GET'])
def random_quote(api_key):
    if check_key(api_key):
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
    else:
        return "Invalid API Key!"


@app.route('/<api_key>/newest', methods=['GET'])
def newest(api_key):
    if check_key(api_key):
        date = request.args.get('date')
        submitter = request.args.get('submitter')

        if date is not None:
            return jsonify(return_json(Quote.query.order_by(Quote.id.desc()).filter_by(date=date).first()))

        elif submitter is not None:
            return jsonify(return_json(Quote.query.order_by(Quote.id.desc()).filter_by(submitter=submitter).first()))

        return jsonify(return_json(Quote.query.order_by(Quote.id.desc()).first()))
    else:
        return "Invalid API Key!"


@auth.oidc_auth
@app.route('/generatekey/<reason>')
def generate_api_key(reason):
    metadata = get_metadata()
    if not check_key_unique(metadata['uid'], reason):
        new_key = APIKey(metadata['uid'], reason)
        db.session.add(new_key)
        db.session.flush()
        db.session.commit()
        return new_key.hash
    else:
        return "There's already a key with this reason for this user!"


def get_metadata():
    uuid = str(session["userinfo"].get("sub", ""))
    uid = str(session["userinfo"].get("preferred_username", ""))
    metadata = {
        "uuid": uuid,
        "uid": uid
    }
    return metadata


def return_json(quote):
    return {
        'quote': quote.quote,
        'submitter': quote.submitter,
        'speaker': quote.speaker,
        'quoteTime': quote.quoteTime,
    }


def parse_as_json(quotes, quote_json=None):
    if quote_json is None:
        quote_json = []
    for quote in quotes:
        quote_json.append(return_json(quote))
    return quote_json


def check_key(api_key, ):
    keys = APIKey.query.filter_by(hash=api_key).all()
    if len(keys) > 0:
        return True


def check_key_unique(owner, reason):
    keys = APIKey.query.filter_by(owner=owner, reason=reason).all()
    if len(keys) > 0:
        return True

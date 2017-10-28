import os
import subprocess
from datetime import datetime

import requests
from flask import Flask, render_template, request, flash, session, make_response, jsonify
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


@app.route('/all')
def index():
    db.create_all()
    quotes = Quote.query.all()  # collect all quote rows in the Quote db

    date = request.args.get('date')
    submitter = request.args.get('submitter')

    if date is not None and submitter is not None:
        quotes = Quote.query.filter_by(quoteTime=date, submitter=submitter)
        return jsonify(parse_as_json(quotes))

    if date is not None:
        quotes = Quote.query.filter_by(quoteTime=date)
        return jsonify(parse_as_json(quotes))

    if submitter is not None:
        quotes = Quote.query.filter_by(submitter=submitter)
        return jsonify(parse_as_json(quotes))

    return jsonify(parse_as_json(quotes))


@app.route('/random')
def random():
    quotes = Quote.query.all()# collect all quote rows in the Quote db

    date = request.args.get('date')
    submitter = request.args.get('submitter')


    if date is not None and submitter is not None:
        quotes = Quote.query.filter_by(quoteTime=date, submitter=submitter)
        return jsonify(parse_as_json(quotes))

    if date is not None:
        quotes = Quote.query.filter_by(quoteTime=date)
        return jsonify(parse_as_json(quotes))

    if submitter is not None:
        quotes = Quote.query.filter_by(submitter=submitter)
        return jsonify(parse_as_json(quotes))

    return jsonify(parse_as_json(quotes))




@app.route('/newest')
def newest():
    date = request.args.get('date')
    submitter = request.args.get('submit')

    if date is not None:
        return jsonify({'cadfad': 'the police'})
    if submitter is not None:
        return jsonify({'friday': 'my dudes'})

    return jsonify({'call': 'the police'})


def parse_as_json(quotes, quote_json=None):
    if quote_json is None:
        quote_json = {}
    for quote in quotes:
        quote_json[quote.id] = {
            'quote': quote.quote,
            'submitter': quote.submitter,
            'speaker': quote.speaker,
            'quoteTime': quote.quoteTime,
        }
    return quote_json

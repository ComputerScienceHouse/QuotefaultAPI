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


@app.route('/')
def index():
    db.create_all()
    quote_json = {}
    quotes = Quote.query.all()  # collect all quote rows in the Quote db
    for quote in reversed(quotes):
        quote_json[quote.id] = {
            'quote': quote.quote,
            'submitter': quote.submitter,
            'speaker': quote.speaker,
            'quoteTime': quote.quoteTime,
        }
    return jsonify(quote_json)


@app.route('/random')
def random():
    date = request.args.get('date')
    submitter = request.args.get('submit')

    if date is not None:
        return jsonify({'cadfad': 'the police'})
    if submitter is not None:
        return jsonify({'friday': 'my dudes'})

    return jsonify({'hello': 'devin'})


@app.route('/newest')
def newest():
    date = request.args.get('date')
    submitter = request.args.get('submit')

    if date is not None:
        return jsonify({'cadfad': 'the police'})
    if submitter is not None:
        return jsonify({'friday': 'my dudes'})

    return jsonify({'call': 'the police'})

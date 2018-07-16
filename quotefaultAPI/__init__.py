import binascii
import json
import os
import random
from datetime import datetime, timedelta

import markdown as markdown
import requests
from flask import Flask, request, jsonify, session
from flask_cors import cross_origin
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
@cross_origin(headers=['Content-Type'])
@check_key(api_key)
def between(start: str, limit: str):
    """
    Shows all quotes submitted between two dates
    :param start: Start date string
    :param limit: End date string
    :return: Returns a JSON list of quotes between the two dates
    """
    submitter = request.args.get('submitter')
    speaker = request.args.get('speaker')
    query = query_builder(start, limit, submitter, speaker)
    if len(query.all()) == 0:
        return "none"
    return parse_as_json(query.all())


@app.route('/<api_key>/create', methods=['PUT'])
@cross_origin(headers=['Content-Type'])
@check_key(api_key)
def create_quote(api_key: str):
    """
    Put request to create a new Quote
    :return: The new Quote object that was created by the request
    """
    # Gets the body of the request and recieves it as JSON
    data = json.loads(request.data.decode('utf-8'))

    if data['quote'] and data['speaker']:
        quote = data['quote']
        if 'submitter' in data:
            submitter = data['submitter']
        else:
            submitter = APIKey.query.filter_by(hash=api_key).all()[0].owner
        speaker = data['speaker']

        if quote is '' or speaker is '':
            return "You didn't fill in one of your fields. You literally only had two responsibilities, " \
                   "and somehow you fucked them up.", 400
        elif Quote.query.filter(Quote.quote == quote).first() is not None:
            return "That quote has already been said, asshole", 400
        elif len(quote) > 200:
            return "Quote is too long! This is no longer a quote, it's a monologue!", 400
        else:
            # Creates a new quote given the data from the body of the request
            new_quote = Quote(submitter=submitter, quote=quote, speaker=speaker)
            db.session.add(new_quote)
            db.session.flush()
            db.session.commit()
            # Returns the json of the quote
            return jsonify(return_json(new_quote))


@app.route('/<api_key>/all', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@check_key(api_key)
def all_quotes():
    """
    Returns all Quotes in the database
    :return: Returns JSON of all quotes in the Quotefault database
    """
    date = request.args.get('date')
    submitter = request.args.get('submitter')
    speaker = request.args.get('speaker')
    query = query_builder(date, None, submitter, speaker)
    if len(query.all()) == 0:
        return "none"
    return parse_as_json(query.all())


@app.route('/<api_key>/random', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@check_key(api_key)
def random_quote():
    """
    Returns a random quote from the database
    :return: Returns a random quote
    """
    date = request.args.get('date')
    submitter = request.args.get('submitter')
    speaker = request.args.get('speaker')
    quotes = query_builder(date, None, submitter, speaker).all()
    if len(quotes) == 0:
        return "none"
    random_index = random.randint(0, len(quotes))
    return jsonify(return_json(quotes[random_index]))


@app.route('/<api_key>/newest', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@check_key(api_key)
def newest():
    """
    Queries the database for the newest quote, with optional parameters to define submitter or datetime stamp
    :return: Returns the newest quote found during the query
    """
    date = request.args.get('date')
    submitter = request.args.get('submitter')
    speaker = request.args.get('speaker')
    query = query_builder(date, None, submitter, speaker).order_by(Quote.id.desc())
    if len(query.all()) == 0:
        return "none"
    return jsonify(return_json(query.first()))


@app.route('/<api_key>/<qid>', methods=['GET'])
@cross_origin(headers=['Content-Type'])
@check_key(api_key)
def quote_id():
    """
    Queries the database for the specified quote.
    :return: Returns the specified quote if exists, else 'none'
    """
    query = query_builder(id_num = qid)
    if len(query.all()) == 0:
        return "none"
    return jsonify(return_json(query.first()))


@app.route('/generatekey/<reason>')
@auth.oidc_auth
def generate_api_key(reason: str):
    """
    Creates an API key for the user requested.
    Using a reason and the username grabbed through the @auth.oidc_auth call
    :param reason: Reason for the API key
    :return: Hash of the Key or a String stating an error
    """
    metadata = get_metadata()
    if not check_key_unique(metadata['uid'], reason):
        # Creates the new API key
        new_key = APIKey(metadata['uid'], reason)
        # Adds, flushes and commits the new object to the database
        db.session.add(new_key)
        db.session.flush()
        db.session.commit()
        return new_key.hash
    else:
        return "There's already a key with this reason for this user!"


@app.route('/logout')
@auth.oidc_logout
def logout():
    return redirect(url_for('index'), 302)


def get_metadata() -> dict:
    """
    Gets user metadata to return to each route that requests it
    :return: Returns a dict of metadata
    """
    uuid = str(session["userinfo"].get("sub", ""))
    uid = str(session["userinfo"].get("preferred_username", ""))
    metadata = {
        "uuid": uuid,
        "uid": uid
    }
    return metadata


def return_json(quote: Quote):
    """
    Returns a Quote Object as JSON/Dict
    :param quote: The quote object being formatted
    :return: Returns a dictionary of the quote object formatted to return as JSON
    """
    return {
        'id': quote.id,
        'quote': quote.quote,
        'submitter': quote.submitter,
        'speaker': quote.speaker,
        'quoteTime': quote.quoteTime,
    }


def parse_as_json(quotes: list, quote_json=None) -> list:
    """
    Builds a list of Quotes as JSON to be returned to the user requesting them
    :param quotes: List of Quote Objects
    :param quote_json: List of Quote Objects as dicts to return as JSON
    :return: Returns a list of Quote Objects as dicts to return as JSON
    """
    if quote_json is None:
        quote_json = []
    for quote in quotes:
        quote_json.append(return_json(quote))
    return jsonify(quote_json)


def check_key(api_key: str)
    def decorator(func):
        def wrapper():
            keys = APIKey.query.filter_by(hash=api_key).all()
            if len(keys) > 0:
                return func()
            else:
                return "Invalid API Key!", 403
        return wrapper
    return decorator


def check_key_unique(owner: str, reason: str) -> bool:
    keys = APIKey.query.filter_by(owner=owner, reason=reason).all()
    if len(keys) > 0:
        return True


def str_to_datetime(date:str) -> datetime:
    """
    Converts a string in the format mm-dd-yyyy to a datetime object
    :param date: the date string
    :return: a datetime object equivalent to the date string
    """
    return datetime.strptime(date, "%m-%d-%Y")


def query_builder(start: str, end: str, submitter: str, speaker: str, id_num = -1):
    """
    Builds a sqlalchemy query.
    :param start: (optional, unless end provided) The date string for the start of the desired range.
    If end is not provided, start specifies a single day's fiter
    :param end: (optional) The date string for the end of the desired range.
    :param submitter: (optional) The CSH username of the submitter to search for.
    :param id_num: (optional) The id of the quote to access from the database.
    :return: The query as defined by the given parameters
    """
    query = Quote.query

    # If an ID is specified, we only need one quote. Don't bother with the other filtering
    if id_num != -1:
        query.filter_by(id=id_num)
        return query

    if start is not None:
        start = str_to_datetime(start)
        if end is not None:
            end = str_to_datetime(end)
        else:
            end = start + timedelta(1)
        query = query.filter(Quote.quoteTime.between(start, end))
    
    if submitter is not None:
        query = query.filter_by(submitter=submitter)

    if speaker is not None:
        query = query.filter_by(speaker=speaker)
    
    return query


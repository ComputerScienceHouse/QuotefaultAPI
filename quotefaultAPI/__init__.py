from flask import Flask, jsonify

import os

app = Flask(__name__)

# if os.path.exists(os.path.join(os.getcwd(), "config.py")):
#     app.config.from_pyfile(os.path.join(os.getcwd(), "config.py"))
# else:
#     app.config.from_pyfile(os.path.join(os.getcwd(), "config.env.py"))


@app.route('/')
def index():
    return jsonify({'hello': 'world'})


@app.route('/random')
def random():
    return jsonify({'hello': 'devin'})


@app.route('/newest')
def newest():
    return jsonify({'call': 'the police'})

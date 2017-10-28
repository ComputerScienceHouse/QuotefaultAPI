from flask import Flask, jsonify, request

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


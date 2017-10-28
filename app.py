from flask import Flask, jsonify

app = Flask(__name__)


@app.route('/')
def example():
    return jsonify({'hello': 'world'})
@app.route('/random')
def random():
    return jsonify({'hello':'devin'})

@app.route('/newest')
def newest():
    return jsonify({'call':'the police'})


if __name__ == "__main__":
    app.run(debug=False)
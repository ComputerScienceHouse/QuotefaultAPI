from quotefaultAPI import app

if __name__ == '__main__':
    # app.run(host=app.config['IP'], port=app.config['PORT'], debug=True)
    app.run(debug=True)

application = app

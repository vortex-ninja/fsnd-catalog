from flask import Flask

app = Flask(__name__)


@app.route('/')
def showRestaurants():
    return 'This page will show all my restaurants'


if __name__ == '__main__':
    app.secret_key = 'Top secret key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

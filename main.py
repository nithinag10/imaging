from flask import Flask, render_template
from flask import jsonify
import socket

app = Flask(__name__)

# two decorators, same function
@app.route('/')
@app.route('/index.html')
def index():
    return "Its working"


if __name__ == '__main__':
    app.run(debug=True)

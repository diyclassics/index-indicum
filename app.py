import os
from flask import Flask, render_template

from pprint import pprint

app = Flask(__name__)
#app.config.from_object(os.environ['APP_SETTINGS'])

@app.route('/')
def homepage():
    pass
#    return render_template('index.html')

@app.route('/authors')
def get_authors():
    pass
#    return render_template('authors.html')

if __name__ == '__main__':
    app.run()

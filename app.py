import os
from flask import Flask, render_template


app = Flask("Index Indicum")
@app.route('/')
def homepage():
    return render_template('isaw_index_indicum.html')


if __name__ == '__main__':
    app.run()
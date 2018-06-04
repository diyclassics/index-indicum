import os
from flask import Flask, render_template
import requests
from lxml import html

app = Flask(__name__)
# app.config.from_object(os.environ['APP_SETTINGS'])


@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/authors')
def get_authors():
    authors = []
    for i in range(1, 14):
        url = 'http://dlib.nyu.edu/awdl/isaw/isaw-papers/'+str(i)+'/'
        page = requests.get(url)
        html_content = html.fromstring(page.content)
        author_elements = html_content.xpath('//meta[@name="DC.creator"]')
        for author in author_elements:
            authors.append(author.attrib['content'])
    return render_template('author.html', authors=authors)


if __name__ == '__main__':
    app.run()

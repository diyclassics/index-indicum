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
        
        authors += html_content.xpath('//span[@rel="dcterms:creator"]//text()')
        authors += html_content.xpath('//span[contains(@property, "dcterms:creator")]/text()')
        authors += html_content.xpath('//h2[contains(@property, "dcterms:creator")]/text()')

        print(authors)

    return render_template('author.html', authors=authors)


if __name__ == '__main__':
    app.run()

import os
from flask import Flask, render_template

import requests
from lxml import html
import re
from nameparser import HumanName


app = Flask(__name__)
app.debug = True
# app.config.from_object(os.environ['APP_SETTINGS'])

BASE_URL = 'http://dlib.nyu.edu/awdl/isaw/isaw-papers/'
PAPERS_URLS = [f'{BASE_URL}{i}' for i in range(1,14)]

# Helper functions
def _sort_names(names):
    # Should check for 'last' in keys
    parsed_names = [HumanName(name) for name in names]
    return [' '.join(name) for name in sorted(parsed_names, key=lambda x: x['last'])]

#def _update_cash() :
# NOT WORKING : the files are too big
#    for i, url in enumerate(PAPERS_URLS, 1):
#        page = requests.get(url)
#        html_content = page.text
#        with open("data/papers/isaw-papers-%s.xhtml"%(i),"w") as paper:
#            paper.write(str(html_content))

#_update_cash()

# Routes
@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/authors')
def get_authors():

    authors_data = dict()
    for i, url in enumerate(PAPERS_URLS, 1):
        page = requests.get(url)
        html_content = html.fromstring(page.content)
        a1 = html_content.xpath('//span[@rel="dcterms:creator"]//text()')
        a2 = html_content.xpath('//span[contains(@property, "dcterms:creator")]/text()')
        a3 = html_content.xpath('//h2[contains(@property, "dcterms:creator")]/text()')
        a = _sort_names(list(set(a1+a2+a3)))
        authors_data[f'ISAW Papers {i}'] = a
    return render_template('author.html', authors_data=authors_data)


@app.route('/authors_reversed')
def get_papers():
    authors_papers = dict()
    for i, url in enumerate(PAPERS_URLS, 1):
        page = requests.get(url)
        html_content = html.fromstring(page.content)
        authors = html_content.xpath('//span[@rel="dcterms:creator"]//text()')
        authors += html_content.xpath('//span[contains(@property, "dcterms:creator")]/text()')
        authors += html_content.xpath('//h2[contains(@property, "dcterms:creator")]/text()')
        authors = list(set(_sort_names(authors)))
        for author in authors :
            try :
                authors_papers[author]["articles"].append(str(i))
            except KeyError :
                try :
                    authors_papers[author]["article"] = list()
                except KeyError :
                    authors_papers[author] = dict()
                    authors_papers[author]["articles"] = list()
                authors_papers[author]["articles"].append(str(i))
            authors_papers[author]["viaf"] = html_content.xpath('//span[@rel="dcterms:creator"]/a[.="%s"]/@href'%author)
    return render_template('author_reversed.html', authors_papers=authors_papers, BASE_URL=BASE_URL)


@app.route('/places')
def get_places():

    places_data = dict()
    for i, url in enumerate(PAPERS_URLS, 1):
        page = requests.get(url)
        html_content = html.fromstring(page.content)
        place_name = html_content.xpath('//a[starts-with(@href,"https://pleiades.stoa.org/place")]/text()')
        place_pleiades = html_content.xpath('//a[starts-with(@href,"https://pleiades.stoa.org/place")]/@href')
        places = list()
        for j in range(len(place_name)):
            places += [place_name[j] + ": " + place_pleiades[j]]
            places = list(set(places))
            places.sort()
        if places:
            places_data[f'ISAW Papers {i}'] = places
    return render_template('places.html', places_data=places_data)

if __name__ == '__main__':
    app.run()
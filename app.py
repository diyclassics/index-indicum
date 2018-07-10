import os
from flask import Flask, render_template, flash
import requests
from lxml import html
import re
from nameparser import HumanName
from tqdm import tqdm #for progress bar
from lxml.etree import tostring
import math

# Imports

import os

import xml.etree.ElementTree as ET
import json
import requests

from collections import Counter, defaultdict
import random

from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from nltk import pos_tag
from nltk.chunk import conlltags2tree
from nltk.tree import Tree
import folium

from pprint import pprint
from tqdm import tqdm #for progress bar


from flask_cors import CORS
from lxml.etree import tostring



app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = "This key need to be changed and kept secret"

app.debug = True
# app.config.from_object(os.environ['APP_SETTINGS'])

BASE_URL = 'http://dlib.nyu.edu/awdl/isaw/isaw-papers/'
PAPERS_URLS = [f'{BASE_URL}{i}' for i in range(1,14)]

# Helper functions
def _sort_names(names):
    # Should check for 'last' in keys
    parsed_names = [HumanName(name) for name in names]
    return [' '.join(name) for name in sorted(parsed_names, key=lambda x: x['last'])]

def _update_cash() :
    for i, url in enumerate(PAPERS_URLS, 1):
        page = requests.get(url)
        html_content = page.text
        with open("data/papers/isaw-papers-%s.xhtml"%(i),"w") as paper:
            paper.write(str(html_content))

# Uncomment inorder to get the newest verion of the articles
# _update_cash()

# Routes
@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/authors')
def get_authors():
    authors_data = dict()
    for i, url in enumerate(PAPERS_URLS, 1):
        with open("data/papers/isaw-papers-%s.xhtml" % (i), "r") as paper:
            html_content = html.parse(paper)
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
        with open("data/papers/isaw-papers-%s.xhtml" % (i), "r") as paper:
            html_content = html.parse(paper)
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
        with open("data/papers/isaw-papers-%s.xhtml" % (i), "r") as paper:
            html_content = html.parse(paper)
        place_name = html_content.xpath('//a[starts-with(@href,"https://pleiades.stoa.org/place")]/text()')
        place_pleiades = html_content.xpath('//a[starts-with(@href,"https://pleiades.stoa.org/place")]/@href')
        places = list()
        for j in range(len(place_name)):
            data = requests.get(place_pleiades[j] + "/json")
            try :
                coordinates = data.json()['features'][0]['geometry']['coordinates']
            except :
                coordinates = []
            places += [place_name[j] + ": " + place_pleiades[j] + " (" + str(coordinates) + ")"]
            places = list(set(places))
            places.sort()
        if places:
            places_data[f'ISAW Papers {i}'] = places
    return render_template('places.html', places_data=places_data)

def places_dict(html_contents, i):
    for html_content in html_contents :
        places = dict()
        place_name = html_content.xpath('//a[starts-with(@href,"https://pleiades.stoa.org/place")]/text()')
        place_pleiades = html_content.xpath('//a[starts-with(@href,"https://pleiades.stoa.org/place")]/@href')

        for j in range(len(place_name)):
            data = requests.get(place_pleiades[j] + "/json")
            place_pid = html_content.xpath('//a[starts-with(@href,"%s")]/ancestor::p/@id' % place_pleiades[j])
            place_captionid = (html_content.xpath('//a[starts-with(@href,"%s")]/ancestor::figure/@id' % place_pleiades[j]))
            for place in place_captionid :
                place_pid.append(place)
            text_pid_list = html_content.xpath('//a[starts-with(@href,"%s")]/ancestor::p' % place_pleiades[j])
            text_captionid_list = html_content.xpath('//a[starts-with(@href,"%s")]/ancestor::figure' % place_pleiades[j])

            for text in text_captionid_list :
                text_pid_list.append(text)
            for k, texte in enumerate(text_pid_list) :
                text_pid = ""
                for t in texte :
                    t = tostring(t, encoding="unicode")
                    text_pid += t
                text_pid_list[k] = text_pid.replace('\n', '').replace("'", '"')
                text_pid_list[k] = (text_pid_list[k]).split(place_name[j])
                text_pid_list[k][0] = text_pid_list[k][0].split(" ")
                bracket_before = False
                bracket_after = False
                if len(text_pid_list[k][0]) > 100:
                    bracket_before = True

                if len(text_pid_list[k]) > 1 :
                    text_pid_list[k][1] = text_pid_list[k][1].split(" ")
                    if len(text_pid_list[k][1]) > 100:
                        bracket_after = True
                    text_pid_list[k] = text_pid_list[k][0][-100:] + ["<b>" + place_name[j] + "</b>"] + text_pid_list[k][1][:100]
                else :
                    text_pid_list[k] = text_pid_list[k][0][-100:] + ["<b>" + place_name[j]]
                text_pid_list[k] = " ".join(text_pid_list[k])
                incomplete_tags_beginning = re.findall(r"^[^<]*>", text_pid_list[k])
                incomplete_tags_end = re.findall(r"<[^>]*$", text_pid_list[k])
                incomplete_tags = incomplete_tags_beginning + incomplete_tags_end
                for tag in incomplete_tags:
                    text_pid_list[k] = text_pid_list[k].replace(tag, "")
                if bracket_after  :
                    text_pid_list[k] =  text_pid_list[k] + "[...]"
                if bracket_before  :
                    text_pid_list[k] = "[...]" + text_pid_list[k]

            url_pid = list()
            for id in place_pid :
                id = BASE_URL + str(i) + "/#" + id
                url_pid.append(id)
            try :
                coordinates = data.json()['features'][0]['geometry']['coordinates']
                coordinates.reverse()
            except :
                coordinates = []
            if coordinates and type(coordinates[0]) is not list :
                places[place_name[j]] = [place_pleiades[j], str(coordinates), url_pid, [str(i)], text_pid_list]

    return places

@app.route('/map/<article_id>')
@app.route('/<article_id>/map')
@app.route('/map')
def map_places(**kwargs):
    if kwargs :
        with open("data/papers/isaw-papers-%s.xhtml" % (kwargs["article_id"]), "r") as paper:
            html_contents = [html.parse(paper)]
        i = kwargs["article_id"]

        places = places_dict(html_contents, i)
        article = "ISAW Papers " + str(i)
    else :
        article = "ISAW Papers"
        places = dict()
        for i, url in enumerate(PAPERS_URLS, 1):
            with open("data/papers/isaw-papers-%s.xhtml" % (i), "r") as paper:
                html_contents = [html.parse(paper)]
            places_article = places_dict(html_contents, i)
            for k,v in places_article.items() :
                if k in places :
                    for p in places_article[k][2] :
                        places[k][2].append(p)
                        if str(i) not in places[k][3] :
                            places[k][3].append(str(i))
                    places[k][3] = ' and '.join(places[k][3])
                else :
                    places[k] = v
    for k, v in places.items():
        # size of the circle on the map (places[k][5])
        radius = math.log10(len(places[k][2]) + 1) * 150000
        places[k].append(radius)
        if type(places[k][3]) is list:
            places[k][3] = ''.join(places[k][3])

    if not places :
        flash("We do not have any places associated with that article", "warning")
        print("blop")
    return render_template('map.html', places=places, article=article)

st = StanfordNERTagger('./stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
                       './stanford-ner/stanford-ner.jar',

                       encoding='utf-8')

# Functions for putting together with inside-outside-beginning (IOB) logic
# Cf. https://stackoverflow.com/a/30666949
#
# For more information on IOB tagging, see https://en.wikipedia.org/wiki/Inside–outside–beginning_(tagging)


def stanfordNE2BIO(tagged_sent):
    bio_tagged_sent = []
    prev_tag = "O"
    for token, tag in tagged_sent:
        if tag == "O": #O
            bio_tagged_sent.append((token, tag))
            prev_tag = tag
            continue
        if tag != "O" and prev_tag == "O": # Begin NE
            bio_tagged_sent.append((token, "B-"+tag))
            prev_tag = tag
        elif prev_tag != "O" and prev_tag == tag: # Inside NE
            bio_tagged_sent.append((token, "I-"+tag))
            prev_tag = tag
        elif prev_tag != "O" and prev_tag != tag: # Adjacent NE
            bio_tagged_sent.append((token, "B-"+tag))
            prev_tag = tag

    return bio_tagged_sent


def stanfordNE2tree(ne_tagged_sent):
    bio_tagged_sent = stanfordNE2BIO(ne_tagged_sent)
    sent_tokens, sent_ne_tags = zip(*bio_tagged_sent)
    sent_pos_tags = [pos for token, pos in pos_tag(sent_tokens)]

    sent_conlltags = [(token, pos, ne) for token, pos, ne in zip(sent_tokens, sent_pos_tags, sent_ne_tags)]
    ne_tree = conlltags2tree(sent_conlltags)
    return ne_tree



# Function for querying geonames

def geonames_query(location):
    '''
    queries geonames for given location name;
    bounding box variables contain default values
    based on: https://prpole.github.io/location-extraction-georeferencing/
    '''
    # Todo
    # - replace error handling

    baseurl = 'http://api.geonames.org/searchJSON'  # baseurl for geonames
    username = USERNAME  # Keep USERNAME in .env
    json_decode = json.JSONDecoder()  # used to parse json response

    params = {
        'username': username,
        'name_equals': location,
        'orderby': 'relevance',
    }

    response = requests.get(baseurl, params=params)
    response_string = response.text
    parsed_response = json_decode.decode(response_string)
    coordinates = ()
    if 'geonames' in parsed_response.keys():
        countries = list()
        if len(parsed_response['geonames']) > 0:
            for i in range(len(parsed_response['geonames'])):
                if 'countryName' in parsed_response['geonames'][i] :
                    countries.append(parsed_response['geonames'][i]['countryName'])
            top_country = sorted(Counter(countries))[0]
            for country in parsed_response['geonames'] :
                if 'countryName' in country :
                    if country['countryName'] == top_country :
                        coordinates = (country['lat'], country['lng'])
    else:
        coordinates = ('', '')
    return coordinates


@app.route('/ner')
def ner():
    st = StanfordNERTagger('./stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
                           './stanford-ner/stanford-ner.jar',

                           encoding='utf-8')


    with open("data/papers/isaw-papers-%s.xhtml" % (1), "r") as paper:
        html_parsed = html.parse(paper)
        work_cited = html_parsed.xpath('//p[@class="work_cited"]')
        html_parsed = [html_parsed]


    places_set = []
    for html_c in tqdm(html_parsed):
        html_c = tostring(html_c, encoding="unicode")
        for work in work_cited :
            work = tostring(work, encoding="unicode")
            html_c = html_c.replace(work, "")

        tokenized_marc = word_tokenize(html_c)
        classified_marc = st.tag(tokenized_marc)
        classified_marc = [item for item in classified_marc if item[0] != '']  # clean up parsing
        ne_tree = stanfordNE2tree(classified_marc)

        ne_in_sent = []
        for subtree in ne_tree:
            if type(subtree) == Tree:  # If subtree is a noun chunk, i.e. NE != "O"
                ne_label = subtree.label()
                ne_string = " ".join([token for token, pos in subtree.leaves()])
                ne_in_sent.append((ne_string, ne_label))

        locations = set([tag[0] for tag in ne_in_sent if
                         tag[1] == 'LOCATION'])  # If we don't make this a set, we can use frequency info for map weight

        places_set.append(locations)

    places_set = [sorted(item) for item in places_set]

    # Build list of likely coordinates for places

    places_list = []
    map = dict()

    for places in places_set:
        for place in places:
            ll = geonames_query(place)
            if ll != ():
                places_list.append(place)
                ll = list(ll)
                map[place] = list()
                for l in ll :
                    map[place].append((float(l)))
    print(len(map))

    return render_template('map_ner.html', places=map)


if __name__ == '__main__':
    app.run()


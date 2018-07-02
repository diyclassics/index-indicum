
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
from app import app
import folium

from pprint import pprint
from tqdm import tqdm #for progress bar

# Setup Stanford NER Tagger
# Ignore deprecation warning for now; we'll deal with it when the time comes!
USERNAME = 'fmezard'

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

    if 'geonames' in parsed_response.keys():
        if len(parsed_response['geonames']) > 0:
            first_response = parsed_response['geonames'][0]
            coordinates = (first_response['lat'], first_response['lng'])
        else:
            coordinates = ('', '')
    else:
        coordinates = ('', '')
    return coordinates


@app.route('/ner')
def ner():
    st = StanfordNERTagger('./stanford-ner/classifiers/english.all.3class.distsim.crf.ser.gz',
                           './stanford-ner/stanford-ner.jar',

                           encoding='utf-8')


    #with open("data/papers/isaw-papers-%s.xhtml" % (1), "r") as paper:
        #html_content = [paper.read()]
        #print(type(html_content))
    html_content = ["j'aime Paris et Londres !"]
    places_set = []

    for html in tqdm(html_content):
        marc_coordinates = []
        tokenized_marc = word_tokenize(html)
        classified_marc = st.tag(tokenized_marc)
        classified_marc = [item for item in classified_marc if item[0] != '']  # clean up parsing
        ne_tree = ner.stanfordNE2tree(classified_marc)

        ne_in_sent = []
        for subtree in ne_tree:
            if type(subtree) == ner.Tree:  # If subtree is a noun chunk, i.e. NE != "O"
                ne_label = subtree.label()
                ne_string = " ".join([token for token, pos in subtree.leaves()])
                ne_in_sent.append((ne_string, ne_label))

        locations = set([tag[0] for tag in ne_in_sent if
                         tag[1] == 'LOCATION'])  # If we don't make this a set, we can use frequency info for map weight

        places_set.append(locations)

    places_set = [sorted(item) for item in places_set]
    print(places_set)

    # Build list of likely coordinates for places

    places_list = []
    coordinates_list = []

    for places in places_set:
        coordinates = []
        for place in places:
            ll = ner.geonames_query(place)
            if ll != ('', ''):
                places_list.append(place)
                coordinates.append(ll)
        coordinates_list.append(coordinates)


    coordinates_list = [[(float(lat), float(long)) for lat, long in item] for item in coordinates_list]

    print(coordinates_list[0])
    return render_template('index.html')
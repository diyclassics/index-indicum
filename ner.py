from constants import USERNAME

import os
import json
import requests
from collections import Counter, defaultdict
from nltk import pos_tag
from nltk.chunk import conlltags2tree


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
                if 'countryName' in parsed_response['geonames'][i]:
                    countries.append(parsed_response['geonames'][i]['countryName'])
            top_country = sorted(Counter(countries))[0]
            for country in parsed_response['geonames']:
                if 'countryName' in country:
                    if country['countryName'] == top_country:
                        coordinates = (country['lat'], country['lng'])
    else:
        coordinates = ('', '')
    return coordinates


def stanfordNE2tree(ne_tagged_sent):
    bio_tagged_sent = stanfordNE2BIO(ne_tagged_sent)
    sent_tokens, sent_ne_tags = zip(*bio_tagged_sent)
    sent_pos_tags = [pos for token, pos in pos_tag(sent_tokens)]

    sent_conlltags = [(token, pos, ne) for token, pos, ne in zip(sent_tokens, sent_pos_tags, sent_ne_tags)]
    ne_tree = conlltags2tree(sent_conlltags)
    return ne_tree

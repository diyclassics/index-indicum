from lxml import html
import requests
from lxml.etree import tostring
import re
import json

BASE_URL = 'http://dlib.nyu.edu/awdl/isaw/isaw-papers/'

PAPERS_URLS = [f'{BASE_URL}{i}' for i in range(1,14)]
def places_dict():
    places = dict()
    for i, url in enumerate(PAPERS_URLS, 1):
        with open("data/papers/isaw-papers-%s.xhtml" % (i), "r") as paper:
            html_contents = [html.parse(paper)]
        for html_content in html_contents :
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
                    if bracket_after:
                        text_pid_list[k] = text_pid_list[k] + "[...]"
                    if bracket_before:
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
    print(places)
    return places


places = places_dict()

with open("data/places.json", "w") as data_places:
    data_places.write(json.dumps(places))
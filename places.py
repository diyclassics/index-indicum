from constants import BASE_URL

import json
import requests
from lxml.etree import tostring
import re


def places_dict(html_contents, i):
    '''
    Function creating the dict with all the information for the creation of the maps
    :param i: number of the article from which we want to take the informations
    :type i: int
    :param html_contents : ISAW Papers page
    :type html_contents : parsed html
    :return places : dictionnary with all the information for the creation of the map
    '''
    for html_content in html_contents :
        places = dict()
        place_name = html_content.xpath('//a[starts-with(@href,"https://pleiades.stoa.org/place")]/text()')
        place_pleiades = html_content.xpath('//a[starts-with(@href,"https://pleiades.stoa.org/place")]/@href')

        for j in range(len(place_name)):

            # Getting the data from pleiades
            data = requests.get(place_pleiades[j] + "/json")

            # Getting all the ids and bringing them in the same list
            place_pid = html_content.xpath('//a[starts-with(@href,"%s")]/ancestor::p/@id' % place_pleiades[j])
            place_captionid = (html_content.xpath('//a[starts-with(@href,"%s")]/ancestor::figure/@id' % place_pleiades[j]))
            for place in place_captionid :
                place_pid.append(place)

            # Getting the text of the paragraphs related to a place
            text_pid_list = html_content.xpath('//a[starts-with(@href,"%s")]/ancestor::p' % place_pleiades[j])
            text_captionid_list = html_content.xpath('//a[starts-with(@href,"%s")]/ancestor::figure' % place_pleiades[j])
            for text in text_captionid_list :
                text_pid_list.append(text)
            for k, texte in enumerate(text_pid_list) :
                text_pid = ""
                for t in texte :
                    t = tostring(t, encoding="unicode")
                    text_pid += t
                # Deleting \n in order to avoid javascript errors
                text_pid_list[k] = text_pid.replace('\n', '').replace("'", '"')
                text_pid_list[k] = (text_pid_list[k]).split(place_name[j])

                # Keeping only the 100 words before and after the name of the place and writing the name of the place in bold
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

                # deleting incomplete tags
                incomplete_tags_beginning = re.findall(r"^[^<]*>", text_pid_list[k])
                incomplete_tags_end = re.findall(r"<[^>]*$", text_pid_list[k])
                incomplete_tags = incomplete_tags_beginning + incomplete_tags_end
                for tag in incomplete_tags:
                    text_pid_list[k] = text_pid_list[k].replace(tag, "")
                if bracket_after  :
                    text_pid_list[k] =  text_pid_list[k] + "[...]"
                if bracket_before  :
                    text_pid_list[k] = "[...]" + text_pid_list[k]

            # building the urls leading to the paragraphs of the articles
            url_pid = list()
            for id in place_pid :
                id = BASE_URL + str(i) + "/#" + id
                url_pid.append(id)

            # taking the coordinates from pleiades json
            try :
                coordinates = data.json()['features'][0]['geometry']['coordinates']
                coordinates.reverse()
            except :
                coordinates = []
            if coordinates and type(coordinates[0]) is not list :
                places[place_name[j]] = [place_pleiades[j], str(coordinates), url_pid, [str(i)], text_pid_list]

    return places
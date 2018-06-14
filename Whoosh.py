#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
Whoosh.py
CS483 - WSU Vancouver Web Data - Instructor: Ben McCamish
Copyright (c) 2017-Present Megan Ramirez, Emmanuel Rebollar, Samuel Serea, Ronald Cotton.
All Rights Reserved.
'''

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.qparser import MultifieldParser
from whoosh.analysis import *
from whoosh.support.charset import accent_map
import urllib  # for HTTP response codes
import os
import folium
import sqlite3
from decimal import Decimal
from jinja2 import Template

# global lists and indexer for flask_server to access
indexer = None
titles = list()
links = list()
images = list()
locations = list()
types = list()
descriptions = list()
y_long = list()
x_lat = list()


def get_indexer():
    '''
    gets the indexer for flask_server
    :return: indexer
    '''
    global indexer
    return indexer


def get_titles():
    '''
    gets titles for flask_server
    :return: titles
    '''
    global titles
    return titles


def get_links():
    '''
    get links for flask_server
    :return: links
    '''
    global links
    return links


def get_images():
    '''
    get images for flask_server
    :return: images
    '''
    global images
    return images


def get_locations():
    '''
    get locations for flask_server
    :return: locations
    '''
    global locations
    return locations


def get_types():
    '''
    get types for flask_server
    :return: types
    '''
    global types
    return types


def get_descriptions():
    '''
    get descriptions for flask_server
    :return: descriptions
    '''
    global descriptions
    return descriptions


def get_lon():
    '''
    get longitudes for flask_server
    :return: longitudes
    '''
    global y_long
    return y_long


def get_lat():
    '''
    get latitudes for flask_server
    :return: latitudes
    '''
    global x_lat
    return x_lat


def convert(degrees, minutes, seconds, direction):
    '''
    converts to longitude or latitudes from dms format
    :param degrees:
    :param minutes:
    :param seconds:
    :param direction:
    :return:
    '''
    result = degrees + minutes / 60 + seconds / 3600
    if direction == 'S' or direction == 'W':
        result *= -1
    return result


def split_coordinate(target):
    '''
    Splits up coordinates and separates by degree, minute, seconds, and directions
    :param target:
    :return:
    '''
    degree = unichr(176)
    single_prime = unichr(8242)
    double_prime = unichr(8243)

    degrees = "0"
    minutes = "0"
    seconds = "0"
    direction = "N"
    degree_present = 0
    single_prime_present = 0
    double_prime_present = 0
    for m in target:
        if m == degree:
            degree_present = 1
        if m == single_prime:
            single_prime_present = 1
        if m == double_prime:
            double_prime_present = 1

    if degree_present == 1 and single_prime_present == 1 and double_prime_present == 1:
        result1 = target.split(degree, 1)
        degrees = result1[0]
        result2 = result1[1].split(single_prime, 1)
        minutes = result2[0]
        result3 = result2[1].split(double_prime, 1)
        seconds = result3[0]
        direction = result3[1]

    elif degree_present == 1 and single_prime_present == 0 and double_prime_present == 0:
        result1 = target.split(degree, 1)
        degrees = result1[0]
        direction = result1[1]

    elif degree_present == 1 and single_prime_present == 1 and double_prime_present == 0:
        result1 = target.split(degree, 1)
        degrees = result1[0]
        result2 = result1[1].split(single_prime, 1)
        minutes = result2[0]
        direction = result2[1]

    value = convert(Decimal(degrees), Decimal(
        minutes), Decimal(seconds), direction)
    return str(round(value, 6)).decode("utf-8")


def escape_filter(words):
    '''
    filters out escape characters so characters print correctly for title and description - convert to javascipt escape
    codes. Also takes care of wikipedia citations
    :param words: original text
    :return: filtered text
    '''
    dict = {'\'': '', '\"': '', '\\': '\\', '\b': '', '\r': '', '\f': '',
            '\t': '', '\v': '', '\n': '', '\u0092': '\\', '[1]': '',
            '[2]': '', '[3]': '', '[4]': '', '[5]': '', '[6]': '', '[7]': '',
            '[8]': '', '[9]': '', '[10]': '', '?': ''}
    for d in dict:
        words = words.replace(d, dict[d])
    return unicode(words)


def abbr_expander(words):
    '''
    expands abbreviations
    :param words: original text
    :return: expands all wordsthat are abbr.
    '''
    dict = {'aly ' : 'alley ', 'byu ': 'bayoo ',
            'bnd ': 'bend ', 'blf ': 'bluff ', 'blvd ': 'boulevard ','byp ': 'bypass ',
            'cp ': 'camp ', 'ave ': 'avenue ', 'ct ': 'court ', 'crk ': 'creek ', 'xing ': 'crossing ',
            'xrd ': 'crossroad ', 'cv ': 'cove ', 'cyn ': 'canyon ', 'dm ':'dam ',
            'ext ': 'extension ','expy ': 'expressway ', 'ft ': 'fort ', 'fwy ': 'freeway ',
            'hbr ': 'harbor ', 'jct ': 'junction ', 'lk ': 'lake ', 'ln ': 'lane ',
            'lndg ': 'landing ', 'ml ': 'mill ', 'mt ': 'mount ', 'mtn ': 'mountain ', 'psge ': 'passage ',
            'pl ': 'place ', 'prt ': 'port ', 'rd ': 'road ', 'rnch ': 'ranch ', 'rte ': 'route ',
            'riv ': 'river ', 'rpds ': 'rapids ', 'un ': 'union ', 'via ': 'viaduct ', 'vl ': 'ville ',
            'wl ': 'well ','ak ': 'alaska ','al ': 'alabama ','ar ': 'arkansas ','az ': 'arizona ',
            'ca ': 'california ','co' : 'colorado ','dc ': 'district of columbia ',
            'de ': 'delaware ','fl ': 'florida ','ga ': 'georgia ','gu ': 'guam ','hi ': 'hawaii ',
            'ia ': 'iowa ','id ': 'idaho ','il ': 'illinois ','in ': 'indiana ','ks ': 'kansas ',
            'ky ': 'kentucky ','la ': 'louisiana ','ma ': 'massachusetts ','md ': 'maryland ',
            'me ': 'maine ','mn ': 'minnesota ','mo ': 'missouri ','mp ': 'northern mariana islands ',
            'ms ': 'mississippi ','na ': 'national ','nc ': 'north carolina ','nd ': 'north dakota ',
            'ne ': 'nebraska ','nh ': 'new hampshire ','nj ': 'new jersey ','nm ': 'new mexico ',
            'nv ': 'nevada ','ny ': 'new york ','oh ': 'ohio ','ok ': 'oklahoma ','or ': 'oregon ',
            'pa ': 'pennsylvania ','pr ': 'puerto rico ','ri ': 'rhode island ','sc ': 'south carolina ',
            'sd ': 'south dakota ','tn ': 'tennessee ','tx ': 'texas ','ut ': 'utah','va ': 'virginia ',
            'vi ': 'virgin islands ','vt ': 'vermont ','wa ': 'washington ','wi ': 'wisconsin ',
            'wv ': 'west virginia ','wy ': 'wyoming '}
    for d in dict:
        words = words.replace(d, dict[d])
    return unicode(words)


def whoosh_search(indexer, searchTerm, waterfall_on, national_park_on, lake_on, mountain_on, lon, lat):
    '''
    conducts whoosh search
    :param indexer:
    :param searchTerm:
    :param waterfall_on:
    :param national_park_on:
    :param lake_on:
    :param mountain_on:
    :param lon:
    :param lat:
    :return:
    '''
    global descriptions, types, locations, images, links, titles, x_lat, y_long

    # Clear these values to populate
    titles = list()
    links = list()
    images = list()
    locations = list()
    types = list()
    descriptions = list()
    x_lat = list()
    y_long = list()

    first = 0
    first_mountain = 0
    first_national_park = 0
    first_lake = 0
    first_waterfall = 0
    strippedSearch = ''
    searchTerm = abbr_expander(searchTerm)

    # Add analyzers
    my_analyzer = RegexTokenizer() | LowercaseFilter() | CharsetFilter(
        accent_map) | StopFilter(renumber=True, lang="en") | StemFilter(
        lang="en")
    for a in my_analyzer(unicode(searchTerm)):
        strippedSearch += a.text + " "

    with indexer.searcher() as searcher:
        # Performs search
        query = MultifieldParser(
            ["title", "description", "location", "type"], schema=indexer.schema).parse(strippedSearch)
        results = searcher.search(query, limit=100)
        print("Length of results: " + str(len(results)))

        for line in results:
            if line['longitude'] is None or line['latitude'] is None:
                continue
            if (line['longitude'] == "0.0") or (line['latitude'] == "0.0"):
                continue

            # Checks for checkboxes to see if we are searching for that type of data
            if (line['type'] == "national park" and national_park_on == "on") or \
                    (line['type'] == "mountain" and mountain_on == "on") or \
                    (line['type'] == "lake" and lake_on == "on") or \
                    (line['type'] == "waterfall" and waterfall_on == "on"):

                tempurl = ""
                if line['images'] != "":
                    mylist = line['images'].split(', ')
                    tempurl = 'http:' + mylist[1]
                else:
                    # put our default images here
                    tempurl = "https://upload.wikimedia.org/wikipedia/commons/2/26/Blank_globe.svg"

                pageurl = line['url']

                # Appends values to ends of lists
                titles.append(escape_filter(line['title']))
                descriptions.append(escape_filter(line['description']))
                images.append(tempurl)
                links.append(pageurl)
                types.append(line['type'])
                y_long.append(line['longitude'])
                x_lat.append(line['latitude'])

                # this is for markers, not part of the list
                longitude = line['longitude']
                latitude = line['latitude']

                # if not lat, long from user clicking link, use first on search
                # new search, new search or no results, see whole map
                if lon is None or lat is None:
                    lon = longitude
                    lat = latitude

                if first == 0:
                    map = folium.Map(width='100%', height='100%', location=[Decimal(lon), Decimal(lat)],
                                     zoom_start=8, max_zoom=16, min_zoom=3)
                    first = 1
                # Adds values into the maps
                if line['type'] == u'mountain':
                    if first_mountain == 0:
                        fg_mountain = folium.FeatureGroup(name="Mountains")
                        first_mountain = 1
                    fg_mountain.add_child(folium.Marker(location=[Decimal(longitude), Decimal(latitude)], popup=(
                        folium.Popup(line['title'])), icon=folium.Icon(color='red', icon_color='gray')))
                if line['type'] == u'national park':
                    if first_national_park == 0:
                        fg_parks = folium.FeatureGroup(
                            name="National Parks")
                        first_national_park = 1
                    fg_parks.add_child(folium.Marker(location=[Decimal(longitude), Decimal(latitude)], popup=(
                        folium.Popup(line['title'])), icon=folium.Icon(color='green', icon_color='gray')))
                if line['type'] == u'lake':
                    if first_lake == 0:
                        fg_lakes = folium.FeatureGroup(name="Lakes")
                        first_lake = 1
                    fg_lakes.add_child(folium.Marker(location=[Decimal(longitude), Decimal(latitude)], popup=(
                        folium.Popup(line['title'])), icon=folium.Icon(color='blue', icon_color='gray')))
                if line['type'] == u'waterfall':
                    if first_waterfall == 0:
                        fg_waterfalls = folium.FeatureGroup(
                            name="Waterfalls")
                        first_waterfall = 1
                    fg_waterfalls.add_child(folium.Marker(location=[Decimal(longitude), Decimal(latitude)], popup=(
                        folium.Popup(line['title'])), icon=folium.Icon(color='purple', icon_color='gray')))
                if first_mountain != 0:
                    map.add_child(fg_mountain)
                if first_national_park != 0:
                    map.add_child(fg_parks)
                if first_lake != 0:
                    map.add_child(fg_lakes)
                if first_waterfall != 0:
                    map.add_child(fg_waterfalls)

        # save only if markers change.
        if first == 0:
            map = folium.Map(width='100%', height='100%',
                             location=[0, 0, 0.0], zoom_start=3)

        print "whoosh_search() done successfully"
        # Close database and commit data added to the index
        map.add_child(folium.LayerControl())
        map.save(outfile='map.html')


def index():
    '''
    whoosh indexer from sqlliteDB
    :return: indexer
    '''
    # analyzer
    my_analyzer = RegexTokenizer() | LowercaseFilter() | CharsetFilter(
        accent_map) | StopFilter(renumber=True, lang="en") | StemFilter(
        lang="en")

    # Create Schema
    schema = Schema(title=TEXT(analyzer=my_analyzer, stored=True), url=TEXT(stored=True),
                    description=TEXT(analyzer=my_analyzer, stored=True), images=TEXT(
                    stored=True), location=TEXT(analyzer=my_analyzer, stored=True),
                    longitude=TEXT(stored=True), latitude=TEXT(stored=True),
                    type=TEXT(analyzer=my_analyzer, stored=True))

    # creates index if it doesn't already exist
    if not os.path.exists("index"):
        os.mkdir("index")

    indexer = create_in("index", schema)
    writer = indexer.writer()

    # Connects to database
    conn = sqlite3.connect('places2.db')
    print "Opened database successfully"

    # grabs all tuples from national parks table and inserts into index
    cursor = conn.execute("SELECT * FROM national_parks")
    for row in cursor:
        writer.add_document(title=row[0], url=row[1], description=row[2], images=row[3], location=row[4],
                            longitude=split_coordinate(row[5]), latitude=split_coordinate(row[6]), type=u"national park")

    cursor = conn.execute("SELECT * FROM mountains")
    for row in cursor:
        writer.add_document(title=row[0], url=row[1], description=row[2], images=row[3], location=row[4],
                            longitude=split_coordinate(row[5]), latitude=split_coordinate(row[6]),
                            type=u"mountain")

    cursor = conn.execute("SELECT * FROM lakes")
    for row in cursor:
        writer.add_document(title=row[0], url=row[1], description=row[2], images=row[3], location=row[4],
                            longitude=split_coordinate(row[5]), latitude=split_coordinate(row[6]),
                            type=u"lake")

    cursor = conn.execute("SELECT * FROM waterfalls")
    for row in cursor:
        writer.add_document(title=row[0], url=row[1], description=row[2], images=row[3], location=row[4],
                            longitude=split_coordinate(row[5]), latitude=split_coordinate(row[6]),
                            type=u"waterfall")

    print "Operation done successfully"
    # Close database and commit data added to the index
    conn.close()
    writer.commit(optimize=True)
    return indexer


def whoosh_setup():
    global indexer
    indexer = index()


def main():
    '''
    Creates index over database
    :return: None
    '''
    global indexer
    indexer = index()
    searchTerm = ""
    print "Enter searches to search the database. To quit type q."
    while(searchTerm != "q"):
        searchTerm = raw_input("Please enter a search: ")
        if searchTerm == "q":
            return
        if len(searchTerm) == 0:
            continue


if __name__ == '__main__':
    main()

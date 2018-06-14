#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
flask_server.py
CS483 - WSU Vancouver Web Data - Instructor: Ben McCamish
Copyright (c) 2017-Present Megan Ramirez, Emmanuel Rebollar, Samuel Serea, Ronald Cotton.
All Rights Reserved.
'''

from flask import Flask, render_template, url_for, request, send_file, redirect
from Whoosh import whoosh_search, whoosh_setup
from Whoosh import get_indexer, get_lat, get_lon, get_titles, get_links, get_images, get_descriptions, get_locations, get_types
import time
import urllib

indexer = None
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route('/', methods=['GET', 'POST'])
def index():
    '''
    Handles initial call to website and displays the search engine after the first search is performed on the welcome
    page
    '''
    if request.method == 'POST':
        data = request.form

        global indexer
        query = data.get('searchterm', '')

        titles = get_titles()
        links = get_links()
        images = get_images()
        locations = get_locations()
        types = get_types()
        descriptions = get_descriptions()

        whoosh_search(indexer, searchterm, "on", "on", "on", "on", 0, 0)

        return render_template('welcome_page.html', query=searchterm,
                               results=zip(titles, descriptions, images, links, "0.0", "0.0"),
                               waterfall_on="on", national_park_on="on", mountain_on="on",
                               lake_on="on")
        return render_template('index.html')

    if request.method == 'GET':
        data = request.args
        return render_template('index.html')


@app.route('/my-link', methods=['GET'])
def my_link():
    ''' Verifies that the link is valid when wikipedia button is clicked if not just sends Wikipedia page does not exist '''
    data = request.args
    value = data.get('my_link')
    print value

    try:
        httpResponse = urllib.urlopen(value)
        if httpResponse.getcode == 404:
            return "Wikipedia page not found"
        else :
            return redirect(value)
    except Exception:
        return "Wikipedia page not available"


@app.route('/map.html')
def show_map():
    ''' Sends the map file '''
    return send_file('map.html')


@app.route('/results/', methods=['GET', 'POST'])
def results():
    '''
    Handles a basic search
    :return:
    '''
    if request.method == 'POST':
        # do more into request to find resolution
        data = request.form
    else:
        data = request.args

    # get query value
    query = data.get('searchterm','')

    # get check mark values
    waterfall_on = data.get('waterfall')
    national_park_on = data.get('national_park')
    mountain_on = data.get('mountain')
    lake_on = data.get('lake')

    print waterfall_on
    print national_park_on
    print mountain_on
    print lake_on

    # get latitude and longitude to set map to it.
    lat = data.get('lat')
    lon = data.get('lon')

    # grab indexer and perform woosh search
    global indexer
    whoosh_search(indexer, query, waterfall_on, national_park_on, lake_on, mountain_on, lon, lat)

    print "You searched for: " + query

    # Get lists that have been set during whoosh search
    titles = get_titles()
    links = get_links()
    images = get_images()
    locations = get_locations()
    types = get_types()
    descriptions = get_descriptions()
    lat = get_lat()
    lon = get_lon()

    print titles

    return render_template('welcome_page.html', query=query, results=zip(titles, descriptions, images, links, lon, lat), waterfall_on=waterfall_on, national_park_on=national_park_on, mountain_on=mountain_on, lake_on=lake_on)

if __name__ == '__main__':
    whoosh_setup()
    indexer = get_indexer()
    app.run(debug=True)

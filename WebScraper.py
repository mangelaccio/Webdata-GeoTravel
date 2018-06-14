#!/usr/bin/env python2
# -*- coding: utf-8 -*-

'''
WebScraper.py
CS483 - WSU Vancouver Web Data - Instructor: Ben McCamish
Copyright (c) 2017-Present Megan Ramirez, Emmanuel Rebollar, Samuel Serea, Ronald Cotton.
All Rights Reserved.
'''

from bs4 import BeautifulSoup
from lxml import etree
import requests
import urllib
import sqlite3
from Whoosh import split_coordinate

# Holds information on all the national parks found
DATABASE_XML = etree.Element('PLACES')
sql_national_parks = ''' INSERT INTO national_parks(title,url,description,image,location,longitude,latitude)
          VALUES(?,?,?,?,?,?,?) '''
sql_waterfalls = ''' INSERT INTO waterfalls(title,url,description,image,location,longitude,latitude)
          VALUES(?,?,?,?,?,?,?) '''
sql_lakes = ''' INSERT INTO lakes(title,url,description,image,location,longitude,latitude)
          VALUES(?,?,?,?,?,?,?) '''
sql_mountains = ''' INSERT INTO mountains(title,url,description,image,location,longitude,latitude)
          VALUES(?,?,?,?,?,?,?) '''


def setAction(whatAction):
    return 'action=' + whatAction + '&'


def setFormat(whatFormat):
    return 'format=' + whatFormat + '&'


def searchFor(searchTerms, limit):
    return 'search=' + searchTerms + '&limit=' + limit + '&'


def titles(whatTitles):
    listOfTitles = ''
    for title in whatTitles:
        listOfTitles += title + "|"
    return 'titles=' + listOfTitles[:-1] + '&'


def getPage(url):
    page = requests.get(url)
    return page


def searchWikiURL(wikiURL, searchTerms, limit):
    return wikiURL + setAction('opensearch') + setFormat('xml') + searchFor(searchTerms, limit)


def queryWikiURL(wikiURL, queryTerms):
    return wikiURL + setAction('query') + setFormat('xml') + titles(queryTerms)


def strip_ns(tree):
    for node in tree.iter():
        try:
            has_namespace = node.tag.startswith('{')
        except AttributeError:
            continue
        if has_namespace:
            node.tag = node.tag.split('}', 1)[1]


def collect_basic_data(TAG_BASE, soup, table, url, sql, conn):
    '''
    Collects, name, description, pictures, location, area, and coordinates
    take HTML file and then stores the information in the xml file.
    :param TAG_BASE:
    :param soup:
    :param table:
    :param url:
    :param sql:
    :param conn:
    :return:
    '''
    spacer = ", "
    # TAG_URL = etree.SubElement(TAG_BASE, 'URL')
    # TAG_URL.text = url
    title = ""
    description = ""
    image = ""
    location = ""
    longitude = ""
    latitude = ""
    # Gets a Description, this is just the first sentence of the article.
    if soup.find('p'):
        # TAG_DESCRIPTION = etree.SubElement(TAG_BASE, 'DESCRIPTION')
        # TAG_DESCRIPTION.text = soup.find('p').text.partition('.')[0] + '.'
        description = soup.find('p').text

    # Gets images
    if table.find('img'):
         # TAG_IMAGE = etree.SubElement(TAG_BASE, 'IMAGE')
        try:
            for a in table.find_all('img'):
                if image is not None:
                    # TAG_IMAGE.text = TAG_IMAGE.text + spacer + a['src']
                    image = image + spacer + a['src']
                else:
                     # TAG_IMAGE.text = a['src']
                    image = a['src']
        except Exception:
            print ""

    for tr in table.find_all('tr'):
        if tr.find('th'):
            # Gets Name
            if tr.find('th', class_='fn org'):
                # TAG_NAME = etree.SubElement(TAG_BASE, 'NAME')
                # TAG_NAME.text = tr.find('th').text
                title = tr.find('th').text

            # Gets location
            elif tr.find('th').text == 'Location':  # Location
                # TAG_LOCATION = etree.SubElement(TAG_BASE, 'LOCATION')
                for a in tr.find('td').find_all('a'):
                    if location is not None:
                        # TAG_LOCATION.text = TAG_LOCATION.text + spacer + a.text
                        location = location + spacer + a.text
                    else:
                      #  TAG_LOCATION.text = a.text
                        location = a.text
                if tr.find('td', class_='locality'):
                    #TAG_LOCATION.text = tr.find('td').text
                    location = tr.find('td').text

            # Get Coordinates
            elif tr.find('th').text == 'Coordinates':
                # TAG_COORDINATES = etree.SubElement(TAG_BASE, 'COORDINATES')
                # TAG_LATITUDE = etree.SubElement(TAG_COORDINATES, 'LATITUDE')
                #TAG_LATITUDE.text = tr.find('span', class_='latitude').text
                longitude = tr.find('span', class_='latitude').text
                # TAG_LONGITUDE = etree.SubElement(TAG_COORDINATES, 'LONGITUDE')
                # TAG_LONGITUDE.text = tr.find('span', class_='longitude').text
                latitude = tr.find('span', class_='longitude').text

    place = (title, url, description, image, location, longitude, latitude)
    insert_row(conn, place, sql)


def check_if_waterfall(soup, url, conn):
    '''
    Checks if url is a waterfall
    :param soup:
    :param url:
    :param conn:
    :return:
    '''
    table = soup.find('table', class_='infobox vcard')
    if table is not None:
        for tr in table.find_all('tr'):
            if tr.find('th'):
                if tr.find('th').text == 'Total height':  # Location
                    collect_basic_data_waterfalls(soup, url, conn)
                    return


def collect_basic_data_waterfalls(soup, url, conn):
    '''
    collects basic data on waterfall
    :param soup:
    :param url:
    :param conn:
    :return:
    '''
    table = soup.find('table', class_='infobox vcard')
    if table is not None:
        TAG_WATERFALL = etree.SubElement(DATABASE_XML, 'WATERFALL')
        collect_basic_data(TAG_WATERFALL, soup, table,
                           url, sql_waterfalls, conn)


def check_if_mountain(soup, url, conn):
    '''
    Checks if url is a mountain
    :param soup:
    :param url:
    :param conn:
    :return:
    '''
    table = soup.find('table', class_='infobox vcard')
    if table is not None:
        for tr in table.find_all('tr'):
            if tr.find('th'):
                if tr.find('th').text == 'Elevation':  # Location
                    collect_basic_data_mountains(soup, url, conn)
                    return


def collect_basic_data_mountains(soup, url, conn):
    '''
    Collects basic data on mountains
    :param soup:
    :param url:
    :param conn:
    :return:
    '''
    table = soup.find('table', class_='infobox vcard')
    if table is not None:
        TAG_MOUNTAIN = etree.SubElement(DATABASE_XML, 'MOUNTAIN')
        collect_basic_data(TAG_MOUNTAIN, soup, table, url, sql_mountains, conn)


def check_if_lake(soup, url, conn):
    '''
    Checks if url is a lake
    :param soup:
    :param url:
    :param conn:
    :return:
    '''
    table = soup.find('table', class_='infobox vcard')
    if table is not None:
        for tr in table.find_all('tr'):
            if tr.find('th'):
                if tr.find('th').text == 'Surface area' or tr.find('th').text == 'surface area' or tr.find('th').text == 'Surface Area':  # Location
                    collect_basic_data_lakes(soup, url, conn)
                    return


def collect_basic_data_lakes(soup, url, conn):
    '''
    Collects basic data on lakes
    :param soup:
    :param url:
    :param conn:
    :return:
    '''
    table = soup.find('table', class_='infobox vcard')
    if table is not None:
        TAG_LAKE = etree.SubElement(DATABASE_XML, 'LAKE')
        collect_basic_data(TAG_LAKE, soup, table, url, sql_lakes, conn)


def collect_basic_data_national_parks(soup, url, conn):
    '''
    Collects basic data on national parks
    :param soup:
    :param url:
    :param conn:
    :return:
    '''
    table = soup.find('table', class_='infobox vcard')
    if table is not None:
        # Make sure it is a national park
        if table.find('a', title='IUCN'):
            TAG_PARK = etree.SubElement(DATABASE_XML, 'PARK')
            collect_basic_data(TAG_PARK, soup, table, url,
                               sql_national_parks, conn)
        else:
            return


def check_if_list_of_parks(soup, conn):
    '''
    Checks if the web page is a list of national parks.
    If it is then it visits all the links on the page and checks if they are
    national parks.
    :param soup:
    :param conn:
    :return:
    '''
    # Wikipedia base website to be concatenated with href of possible national
    # parks found on web page.
    basewiki = "https://en.wikipedia.org"

    try:
        if ("National" in soup.title.text or "national" in soup.title.text) and ("parks" in soup.title.text or "Parks" in soup.title.text) and ("of" in soup.title.text or "Of" in soup.title.text or "in" in soup.title.text or "In" in soup.title.text):
            for a in soup.find_all('a'):
                if a.has_attr('href'):
                    # Checks if reference to another wikipedia page
                    if "/wiki/" in a['href'] and "/" in a['href'][0]:
                        newurl = basewiki + a['href']
                        try:
                            print newurl
                            # Opens and gets new URL's html and checks if it is
                            # a national park
                            r = urllib.urlopen(newurl).read()
                            newSoup = BeautifulSoup(r, "html.parser")
                            collect_basic_data_national_parks(
                                newSoup, newurl, conn)

                        except Exception:
                            continue
    except Exception:
        print ""


def get_waterfalls(soup, conn):
    '''
    Visits all the links on the page
    :param soup:
    :param conn:
    :return:
    '''
    # Wikipedia base website to be concatenated with href
    basewiki = "https://en.wikipedia.org"
    num = 0
    try:
        for a in soup.find_all('a'):
            if a.has_attr('href'):
                # Checks if reference to another wikipedia page
                if "/wiki/" in a['href'] and "/" in a['href'][0] and not "National_Park" in a['href']:
                    newurl = basewiki + a['href']
                    try:
                        print newurl
                        # Opens and gets new URL's html
                        r = urllib.urlopen(newurl).read()
                        newSoup = BeautifulSoup(r, "html.parser")
                        check_if_waterfall(newSoup, newurl, conn)
                        num += 1
                    except Exception:
                        continue
           # if num == 10:
            #    return
    except Exception:
        print ""


def get_lakes(soup, conn):
    '''
    Visits all the links on the page
    :param soup:
    :param conn:
    :return:
    '''
    # Wikipedia base website to be concatenated with href
    basewiki = "https://en.wikipedia.org"
    num = 0
    try:
        for a in soup.find_all('a'):
            if a.has_attr('href'):
                # Checks if reference to another wikipedia page
                if "/wiki/" in a['href'] and "/" in a['href'][0] and not "National_Park" in a['href']:
                    newurl = basewiki + a['href']
                    try:
                        print newurl
                        # Opens and gets new URL's html
                        r = urllib.urlopen(newurl).read()
                        newSoup = BeautifulSoup(r, "html.parser")
                        check_if_lake(newSoup, newurl, conn)
                        num += 1
                    except Exception:
                        continue
                        # if num == 10:
                        #    return
    except Exception:
        print ""


def get_mountains(soup, conn):
    '''
    Visits all the links on the page
    :param soup:
    :param conn:
    :return:
    '''
    # Wikipedia base website to be concatenated with href
    basewiki = "https://en.wikipedia.org"
    num = 0
    try:
        for a in soup.find_all('a'):
            if a.has_attr('href'):
                # Checks if reference to another wikipedia page
                if "/wiki/" in a['href'] and "/" in a['href'][0]:
                    newurl = basewiki + a['href']
                    try:
                        print newurl
                        # Opens and gets new URL's html
                        r = urllib.urlopen(newurl).read()
                        newSoup = BeautifulSoup(r, "html.parser")
                        check_if_mountain(newSoup, newurl, conn)
                        num += 1
                    except Exception:
                        continue
           # if num == 10:
            #    return
    except Exception:
        print ""


def insert_row(conn, place, sql):
    try:
        cur = conn.cursor()
        cur.execute(sql, place)
        conn.commit()
    except Exception as e:
        print e


def main():
    conn = sqlite3.connect('places2.db')
    print "Opened database successfully"
    create_national_parks_table = """ CREATE TABLE IF NOT EXISTS national_parks (
                                           title text PRIMARY KEY ,
                                           url text,
                                           description text,
                                           image text,
                                           location text,
                                           longitude text,
                                           latitude text
                                       ); """
    try:
        c = conn.cursor()
        c.execute(create_national_parks_table)
    except Exception as e:
        print e

    create_national_parks_table = """ CREATE TABLE IF NOT EXISTS waterfalls (
                                           title text PRIMARY KEY ,
                                           url text,
                                           description text,
                                           image text,
                                           location text,
                                           longitude text,
                                           latitude text
                                       ); """
    try:
        c = conn.cursor()
        c.execute(create_national_parks_table)
    except Exception as e:
        print e

    create_national_parks_table = """ CREATE TABLE IF NOT EXISTS lakes (
                                           title text PRIMARY KEY ,
                                           url text,
                                           description text,
                                           image text,
                                           location text,
                                           longitude text,
                                           latitude text
                                       ); """
    try:
        c = conn.cursor()
        c.execute(create_national_parks_table)
    except Exception as e:
        print e

    create_national_parks_table = """ CREATE TABLE IF NOT EXISTS mountains (
                                           title text PRIMARY KEY ,
                                           url text,
                                           description text,
                                           image text,
                                           location text,
                                           longitude text,
                                           latitude text
                                       ); """
    try:
        c = conn.cursor()
        c.execute(create_national_parks_table)
    except Exception as e:
        print e

   # National Parks
    wiki = "https://en.wikipedia.org/w/api.php?"
    wikiURL = searchWikiURL(wiki, 'NationalPark', '1000')
    rawPage = getPage(wikiURL)

    root = etree.fromstring(rawPage.content)
    strip_ns(root)
    siteTitles = root.xpath('/SearchSuggestion/Section/Item/Text/text()')

    print siteTitles
    siteUrls = root.xpath('/SearchSuggestion/Section/Item/Url/text()')
    print siteUrls

    # Checks URLs and and sees if they are national parks. Also checks if it is a list of national parks, and
    # if it is then the program finds national parks on the list.
    for url in siteUrls:
        r = urllib.urlopen(url).read()
        print url
        soup = BeautifulSoup(r, "html.parser")
        collect_basic_data_national_parks(soup, url, conn)
        check_if_list_of_parks(soup, conn)

    # National Parks
    wiki = "https://en.wikipedia.org/w/api.php?"
    wikiURL = searchWikiURL(wiki, 'List of National Parks', '1000')
    rawPage = getPage(wikiURL)

    root = etree.fromstring(rawPage.content)
    strip_ns(root)
    siteTitles = root.xpath('/SearchSuggestion/Section/Item/Text/text()')

    print siteTitles
    siteUrls = root.xpath('/SearchSuggestion/Section/Item/Url/text()')
    print siteUrls

    # Checks URLs and and sees if they are national parks. Also checks if it is a list of national parks, and
    # if it is then the program finds national parks on the list.
    for url in siteUrls:
        r = urllib.urlopen(url).read()
        print url
        soup = BeautifulSoup(r, "html.parser")
        collect_basic_data_national_parks(soup, url, conn)
        check_if_list_of_parks(soup, conn)

    # Lakes
    wiki = "https://en.wikipedia.org/w/api.php?"
    wikiURL = searchWikiURL(wiki, 'List of Lakes', '1000')
    rawPage = getPage(wikiURL)

    root = etree.fromstring(rawPage.content)
    strip_ns(root)
    siteTitles = root.xpath('/SearchSuggestion/Section/Item/Text/text()')

    print siteTitles
    siteUrls = root.xpath('/SearchSuggestion/Section/Item/Url/text()')
    print siteUrls

    for url in siteUrls:
        r = urllib.urlopen(url).read()
        print url
        soup = BeautifulSoup(r, "html.parser")
        get_lakes(soup, conn)

    # Waterfalls
    wiki = "https://en.wikipedia.org/w/api.php?"
    wikiURL = searchWikiURL(wiki, 'List of Waterfalls', '1000')
    rawPage = getPage(wikiURL)

    root = etree.fromstring(rawPage.content)
    strip_ns(root)
    siteTitles = root.xpath('/SearchSuggestion/Section/Item/Text/text()')

    print siteTitles
    siteUrls = root.xpath('/SearchSuggestion/Section/Item/Url/text()')
    print siteUrls

    for url in siteUrls:
        r = urllib.urlopen(url).read()
        soup = BeautifulSoup(r, "html.parser")
        get_waterfalls(soup, conn)

    # Mountains
    wiki = "https://en.wikipedia.org/w/api.php?"
    wikiURL = searchWikiURL(wiki, 'List of Mountains by elevation', '1000')
    rawPage = getPage(wikiURL)

    root = etree.fromstring(rawPage.content)
    strip_ns(root)
    siteTitles = root.xpath('/SearchSuggestion/Section/Item/Text/text()')

    print siteTitles
    siteUrls = root.xpath('/SearchSuggestion/Section/Item/Url/text()')
    print siteUrls

    for url in siteUrls:
        r = urllib.urlopen(url).read()
        soup = BeautifulSoup(r, "html.parser")
        get_mountains(soup, conn)

    # Opens the file and writes the xml to it.
    filename = "data.xml"
    target = open(filename, 'w')
    target.write(etree.tostring(DATABASE_XML, pretty_print=True))
    target.close()

    conn.close()

if __name__ == '__main__':
    main()

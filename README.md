# GeoTravel: Folium-based Search Engine
## Web Data - Assignment 2 - WSU Vancouver
### Python 2/Flask/Whoosh/Folium/SQLite
### Abstract
GeoTravel is a minimalist search engine implemented in Python using various libraries like Whoosh for data indexing, Flask for database interfacing, and Jinja for dynamic web page building. The search engine displays results and information on *lakes, mountains, national parks,* and *waterfalls* as per the user’s query. The data collected in the backend database is scraped from **Wikipedia’s API** and parsed into four data tables built in **SQLite3**, each containing information about their respective topics.

For more information, read the [pdf](docs/CS483_FinalProposal.pdf) documentation found in the **/docs** folder.

![Screenshot: Fuji](screenshots/GeoTravel-Fuji.png)
![Screenshot: Yosemite](screenshots/GeoTravel-Yosemite.png)

### Requirements
Python 2
Imports: Whoosh, urllib, folium, sqlite3, jinja2, flask, beautifulsoup, requests

### Executing
*Note: The webscrapper constructed the SQLite3 database and has been included in this repository*

```sh
    ./flask_server.py
```
or
```sh
    python2 flask_server.py
```

*set browser URL to **localhost:5000** after execution to land on the homepage of GeoTravel.*

Included is the Webscrapping program, [WebScraper.py](WebScraper.py) which takes many hours to process.  Depending on changes to Wikipedia's API and format, the webscrapper may no longer work.

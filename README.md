Open Health Inspections Scraper
==============================

This is a tool to get Virginia restaurant health inspection data from the <a href="http://healthspace.com/Clients/VDH/VDH/web.nsf/home.xsp">HealthSpace</a> website into a database. This is a complete rebuild of v1.0 of the scraper to account for changes in the HealthSpace website and to take advantage of new libraries.

Technical
=========
The scraper is built for Python 3.4. It makes use of the <a href="http://scrapy.org/">Scrapy</a> library. Addresses will be geocoded using the <a href="http://smartystreets.com/">SmartyStreets</a> API. To use SmartyStreets you will need to obtain a key.


To run:

1. Run `pip install -r requirements.txt` to install the necessary dependencies.

2. Run the python 3.x script

	```
	scrapeHealthData.py
	```

license
=======

[Apache 2.0] (https://www.apache.org/licenses/LICENSE-2.0.html)

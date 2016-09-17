Open Health Inspections Scraper
==============================

This is a tool to get Virginia restaurant health inspection data from the <a href="http://healthspace.com/Clients/VDH/VDH/web.nsf/home.xsp">HealthSpace</a> website into a database. This is a complete rebuild of v1.0 of the scraper to account for changes in the HealthSpace website and to take advantage of new libraries.

Technical
=========
The scraper is built for Python 3.4. It makes use of the <a href="http://scrapy.org/">Scrapy</a> library. Addresses will be geocoded using the <a href="http://smartystreets.com/">SmartyStreets</a> API. To use SmartyStreets you will need to obtain a key.


To run:

1. Run `pip install -r requirements.txt` to install the necessary dependencies.

2. Set the following environment variables or use the defaults in `scraper/settings.py`:

   ```
   MONGODB_SERVER
   MONGODB_PORT
   MONGODB_DB
   MONGODB_COLLECTION
   ```

   If you need MongoDB authentication, also set

   ```
   MONGODB_USER
   MONGODB_PWD
   ```
   
   If you want to use the SmartyStreets geocoding integration, also set the following environment variables:

   ```
   SS_ID
   SS_TOKEN
   ```

3. Run the python 3.x script. The scraper can be stopped using `Ctrl/Cmd + C` (only once) and can then be restarted at the point where it stopped. It will save it's progress in the folder specified by the `JOBDIR` setting in `scraper/settings.py`

	```
	scrapeHealthData.py
	```

license
=======

[Apache 2.0] (https://www.apache.org/licenses/LICENSE-2.0.html)

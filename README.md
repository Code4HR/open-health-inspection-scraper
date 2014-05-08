open-health-inspection-scraper
==============================

Tool to get VA restaurant health inspection data from website to database. Addresses are geocoded using the <a href="http://smartystreets.com/">SmartyStreets</a> API. An older version uses the <a href="https://developers.google.com/maps/documentation/geocoding/">Google Geocoding API</a>. To use SmartyStreets you will need to obtain a key. The Google version does not require a key but is limited to 2,500 lookups per 24-hour period.

To run:

1. cd to the `scraper` directory
2. Add `config.json` file with the following content:

    ```
    {"db_uri": "[URI TO MONGODB]",  "db_name":"[NAME OF DATABASE]",
	 "ss_id": "[SmartyStreets ID]", "ss_token":"[SmartyStreets Token]"}
    ```

3. Run the python 2.x script


	```
	python scrapeHealthData.py
	```

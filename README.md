open-health-inspection-scraper
==============================

Tool to get VA restaurant health inspection data from website to database.

To run:

1. cd to the `scraper` directory
2. Add `config.json` file with the following content:

    ```
    {"db_uri":"[URI TO MONGODB]","db_name":"[NAME OF DATABASE]"}
    ```

3. Run the python 2.x script


	```
	python scrapeHealthData.py
	```

# psd-scraper
Python scraper for the [PS Website](http://psd.bits-pilani.ac.in) of BITS Pilani.

Requires `requests` and `beatifulsoup4`
In order to execute this

Clone the repo

create a config.json file by copying the contents from sample_config.json file and updating the email and password fields

run python psd_scrape.py

then run python jsontocsv.py

then data.csv file is generated, this file contains the relevant data

The fields are in order Station Id, Company Name, Domain,  Stipend, City, Total Seats, Project1, Project2, Project3, ...

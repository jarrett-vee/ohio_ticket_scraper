# Ohio Ticket Scraper

This script allows you to scrape specific case details from ohioticketpayments.com for a given date range. The scraped details include the date of offense, the officer's name, the ticket number, and the location of the offense (this could be expanded upon as you see fit).

Features:

Scrapes the data based on a customizable date range.
Saves the extracted data into a CSV file.
Prints out the number of times an officer's name and the defendant's name (top three highest appearers) appeared on the console.
Supports changing the city for which the data is scraped (default is "Brecksville").
Prerequisites
Ensure you have the following Python libraries installed:

Install them via pip:
```
pip install requests beautifulsoup4 pandas
```

How to Use:

Set the date range for which you want to collect the data by editing the start_date and end_date variables in the script.

If you wish to scrape data for a different city other than "Brecksville", replace "Brecksville" in the url variable with the desired city.


Run the script:
```
python policeScraper.py
```

Upon execution, the script will start scraping the data and will save the details in a CSV file named case_data.csv by default. This name can be changed in the script.

Once completed, the script will print the number of appearances for each officer on the console.

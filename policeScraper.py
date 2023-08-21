import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import csv
import time

# This will fetch the date of offense, the officer's name, the ticket number and the location. 
# It will also print out the number of times an officer's name appeared (In console, not in the csv.)

def fetch_case_details(case_num, record_num, num_cases, rnd_value):
    data = {
        'Remote': '1',
        'FunctionName': 'ShowCaseDetail',
        'CaseNum': case_num,
        'RecordNum': str(record_num),
        'NumCases': str(num_cases),
        'RND': str(rnd_value),
        'EndRequest': '1'
    }
    response = requests.post(url, headers=headers, data=data)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

# Set the URL and headers
url = 'https://www.ohioticketpayments.com/Brecksville/MCOnlineServices.php'
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-type': 'application/x-www-form-urlencoded',
    'Cookie': 'PHPSESSID=edf8c541c64f1fc0f2aa8cfb3bc59664',
    'Host': 'www.ohioticketpayments.com',
    'Origin': 'https://www.ohioticketpayments.com',
    'Referer': 'https://www.ohioticketpayments.com/Brecksville/DocketSearch.php',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}
# Set the date range for data collection - note that these dates are customizable.
start_date = datetime.strptime("2023-01-01", "%Y-%m-%d")
end_date = datetime.strptime("2023-01-05", "%Y-%m-%d")

print("Starting data collection from:", start_date.strftime("%Y-%m-%d"), "to:", end_date.strftime("%Y-%m-%d"))

# Initialize the CSV file and timer
csv_filename = "case_data1.csv"
start_time = time.time()

# Initialize a dictionary to store officer appearances
officer_appearances = {}

# Open the CSV file for writing
with open(csv_filename, mode="w", newline="", encoding="utf-8") as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(["DateOfOffense", "OfficerName", "TicketNumber", "Location"])  # Added "Location"

    current_date = start_date
    while current_date <= end_date:
    # CaseType can take on the following attributes: CRA (Felony), CRB (Misdemeanor), TRC (OVI), OTH (Other), and TRD (Other Traffic)
        base_data = {
            'Remote': '1',
            'FunctionName': 'Search',
            'FirstName': '',
            'LastName': '',
            'Waiverable': 'Any Waiverable Status',
            'TicketNumber': '',
            'CaseNumber': '',
            'CaseType': 'All Case Types',
            'DateOfOffense': current_date.strftime("%Y-%m-%d"),
            'CourtDate': 'Any Date',
            'StartAt': '0',
            'RND': '671742',
            'EndRequest': '1'
        }
    
        response = requests.post(url, headers=headers, data=base_data)
        soup = BeautifulSoup(response.content, 'html.parser')
        rows_with_case_details = soup.find_all('tr', onclick=True)
        
        for row in rows_with_case_details:
            onclick_attr = row["onclick"]
            details = onclick_attr.split("ShowCaseDetail(")[1].split(")")[0].replace("'", "").split(",")

            case_num = details[0].strip() if len(details) > 0 else None
            record_num = details[1].strip() if len(details) > 1 else None
            num_cases = details[2].strip() if len(details) > 2 else None
            rnd_value = details[3].strip() if len(details) > 3 else None

            case_soup = fetch_case_details(case_num, record_num, num_cases, rnd_value)
            
            # Extracting Location
            location_row = case_soup.find('td', text='Location: ')
            location_data_td = location_row.find_next_sibling('td', class_='OffenseData') if location_row else None
            location = location_data_td.text.strip() if location_data_td else None
            
            officer_rows = case_soup.find_all('td', text='Officer:')
            officers_in_case = set()

            for officer_row in officer_rows:
                officer_name_td = officer_row.find_next_sibling('td', class_='OffenseData')
                ticket_no_td = officer_row.find_next('td', text='Ticket No:').find_next_sibling('td', class_='OffenseData')
                if officer_name_td and ticket_no_td:
                    officer_name = officer_name_td.text.strip()
                    ticket_no = ticket_no_td.text.strip()
                # ... [rest of officer details extraction]
                if officer_name and officer_name not in officers_in_case:
                    csv_writer.writerow([base_data['DateOfOffense'], officer_name, ticket_no, location])  # Added location
                    officers_in_case.add(officer_name)

                    # Count officer appearances
                    if officer_name in officer_appearances:
                        officer_appearances[officer_name] += 1
                    else:
                        officer_appearances[officer_name] = 1

        current_date += timedelta(days=1)

end_time = time.time()
elapsed_time = end_time - start_time

sorted_officer_appearances = sorted(officer_appearances.items(), key=lambda x: x[1], reverse=True)

# Print officer appearances
print("\nOfficer Appearances:")
for officer_name, count in sorted_officer_appearances:
    print(f"{officer_name}'s name appeared {count} times")

# Print completion message
print("\nData collection completed in {:.2f} seconds and saved to {}".format(elapsed_time, csv_filename))



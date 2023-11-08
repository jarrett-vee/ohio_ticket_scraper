import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# This will fetch the date of offense, the officer's name, the ticket numbert, the location, and the defendant name. 
# It will also print out the number of times an officer's name and the defendant's name (In console, not in the csv.)

session = requests.Session()
start_date = datetime.strptime("2023-01-01", "%Y-%m-%d")
end_date = datetime.strptime("2023-01-05", "%Y-%m-%d")
officer_appearances = {}
defendant_appearances = {}
data_df = pd.DataFrame(columns=["DateOfOffense", "OfficerName", "TicketNumber", "Location", "DefendantName"])

# Set the URL and headers
url = 'https://www.ohioticketpayments.com/Brecksville/MCOnlineServices.php'
headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'www.ohioticketpayments.com',
    'Origin': 'https://www.ohioticketpayments.com',
    'Referer': 'https://www.ohioticketpayments.com/Brecksville/MCOnlineServices.php',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}

def fetch_case_details(case_num, record_num, num_cases, rnd_value, session, url, headers):
    data = {
        'Remote': '1',
        'FunctionName': 'ShowCaseDetail',
        'CaseNum': case_num,
        'RecordNum': str(record_num),
        'NumCases': str(num_cases),
        'RND': str(rnd_value),
        'EndRequest': '1'
    }
    response = session.post(url, headers=headers, data=data)
    soup = BeautifulSoup(response.content, 'html.parser')
    return soup

# Data collection loop
current_date = start_date
while current_date <= end_date:
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

    response = session.post(url, headers=headers, data=base_data)
    soup = BeautifulSoup(response.content, 'html.parser')
    rows_with_case_details = soup.find_all('tr', onclick=True)

    for row in rows_with_case_details:
        onclick_attr = row.get("onclick", "")
        details = onclick_attr.split("ShowCaseDetail(")[1].split(")")[0].replace("'", "").split(",")

        case_num = details[0].strip() if len(details) > 0 else None
        record_num = details[1].strip() if len(details) > 1 else None
        num_cases = details[2].strip() if len(details) > 2 else None
        rnd_value = details[3].strip() if len(details) > 3 else None

        case_soup = fetch_case_details(case_num, record_num, num_cases, rnd_value, session, url, headers)
        
        location_row = case_soup.find('td', string='Location: ')
        location_data_td = location_row.find_next_sibling('td') if location_row else None
        location = location_data_td.text.strip() if location_data_td else None

        defendant_label_td = case_soup.find('td', string='Defendant Name: ')
        defendant_name_td = defendant_label_td.find_next_sibling('td') if defendant_label_td else None
        defendant_name = defendant_name_td.text.strip() if defendant_name_td else None
        
        officer_rows = case_soup.find_all('td', string='Officer:')
        officers_in_case = set()

        for officer_row in officer_rows:
            officer_name_td = officer_row.find_next_sibling('td')
            ticket_no_td = officer_row.find_next('td', string='Ticket No:').find_next_sibling('td')
            if officer_name_td and ticket_no_td:
                officer_name = officer_name_td.text.strip()
                ticket_no = ticket_no_td.text.strip()
                if officer_name and officer_name not in officers_in_case:
                    new_row = pd.DataFrame({
                        "DateOfOffense": [current_date.strftime("%Y-%m-%d")],
                        "OfficerName": [officer_name],
                        "TicketNumber": [ticket_no],
                        "Location": [location],
                        "DefendantName": [defendant_name]
                    })
                    data_df = pd.concat([data_df, new_row], ignore_index=True)
                    officers_in_case.add(officer_name)

                    # Count officer and defendant appearances
                    officer_appearances[officer_name] = officer_appearances.get(officer_name, 0) + 1
                    defendant_appearances[defendant_name] = defendant_appearances.get(defendant_name, 0) + 1

    current_date += timedelta(days=1)

# Process and print officer and defendant appearances in console
sorted_officer_appearances = pd.Series(officer_appearances).sort_values(ascending=False)
sorted_defendant_appearances = pd.Series(defendant_appearances).sort_values(ascending=False)

print("Officer Appearances:")
print(sorted_officer_appearances.to_string())
print("\nTop 3 Most Frequent Defendant Names:")
print(sorted_defendant_appearances.head(3).to_string())

# Save to a csv.
data_df.to_csv('offense_data.csv', index=False)

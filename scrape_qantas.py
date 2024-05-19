import requests
import re
import csv
from datetime import datetime, timedelta

# Function to scrape hotel rates for a given date combination
def scrape_hotel_rates(check_in, check_out):
    url = 'https://www.qantas.com/hotels/properties/18482'
    params = {
        'adults': 2,
        'checkIn': check_in,
        'checkOut': check_out,
        'children': 0,
        'infants': 0,
        'location': 'London, England, United Kingdom',
        'page': 1,
        'payWith': 'cash',
        'searchType': 'list',
        'sortBy': 'popularity'
    }
    response = requests.get(url, params=params)

    if response.status_code == 200:
        webpage_content = response.text
        rates = []

        room_pattern = re.compile(r'<div class="css-1ca2hp6-Hide e1yh5p93">(.*?)</div>', re.DOTALL)
        rate_pattern = re.compile(
            r'<div class="rate-class">.*?<span class="rate-name">(.*?)</span>.*?<span class="guests">(.*?)</span>.*?<span class="cancellation-policy">(.*?)</span>.*?<span class="price">(.*?)</span>.*?<span class="currency">(.*?)</span>.*?</div>',
            re.DOTALL
        )
        top_deal_pattern = re.compile(r'class=".*?top-deal.*?"')

        for room_match in room_pattern.finditer(webpage_content):
            room_content = room_match.group(1)
            room_name_match = re.search(r'<h3 class="css-19vc6se-Heading-Heading-Text e13es6xl3">(.*?)</h3>', room_content)
            if room_name_match:
                room_name = room_name_match.group(1).strip()
            else:
                continue

            for rate_match in rate_pattern.finditer(room_content):
                rate_name = rate_match.group(1).strip()
                number_of_guests = rate_match.group(2).strip()
                cancellation_policy = rate_match.group(3).strip()
                price = rate_match.group(4).strip()
                currency = rate_match.group(5).strip()
                top_deal = bool(top_deal_pattern.search(rate_match.group(0)))

                rate_info = {
                    "Room_name": room_name,
                    "Rate_name": rate_name,
                    "Number_of_Guests": number_of_guests,
                    "Cancellation_Policy": cancellation_policy,
                    "Price": price,
                    "Is_Top_Deal": top_deal,
                    "Currency": currency
                }
                rates.append(rate_info)
        return rates
    else:
        print(f"Failed to retrieve the webpage for dates {check_in} to {check_out}. Status code: {response.status_code}")
        return []

# Generate date combinations for check-in and check-out
def generate_date_combinations(start_date, num_combinations):
    date_combinations = []
    current_date = datetime.strptime(start_date, '%Y-%m-%d')
    for _ in range(num_combinations):
        check_in = current_date.strftime('%Y-%m-%d')
        check_out = (current_date + timedelta(days=1)).strftime('%Y-%m-%d')
        date_combinations.append((check_in, check_out))
        current_date += timedelta(days=2)  # Increment the date by 2 days to get the next combination
    return date_combinations

# Main code
hotel_id = 18482
start_date = '2024-06-02'
num_combinations = 25

date_combinations = generate_date_combinations(start_date, num_combinations)
all_rates = []

for check_in, check_out in date_combinations:
    rates = scrape_hotel_rates(check_in, check_out)
    for rate in rates:
        rate.update({'hotels_id': hotel_id, 'check_in': check_in, 'check_out': check_out})
        all_rates.append(rate)

# Write data to a CSV file
with open('hotel_rates.csv', 'w', newline='') as csvfile:
    fieldnames = ['hotels_id', 'check_in', 'check_out', 'Room_name', 'Rate_name', 'Number_of_Guests',
                  'Cancellation_Policy', 'Price', 'Is_Top_Deal', 'Currency']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for rate in all_rates:
        writer.writerow(rate)

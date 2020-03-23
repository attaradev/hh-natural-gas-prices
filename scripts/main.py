from bs4 import BeautifulSoup
from pathlib import Path
import requests
import csv

data_folder = Path(__file__).parent/'../data/'


def fetch_page(url):
    base_url = 'https://www.eia.gov/dnav/ng/hist/'
    response = requests.get(base_url + url)
    return BeautifulSoup(response.content, 'html.parser')


def get_daily_data(link):
    page = fetch_page(link)
    dates = page.find_all(class_='B6')
    data_rows = [td.find_parent('tr') for td in dates]

    with open(data_folder/'daily.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Price'])
        for data_row in data_rows:
            week, *values = [td.get_text() for td in data_row.find_all('td')]
            week = week.strip()
            values = [x if x != '' else '0.00' for x in values]
            year = week[:4]
            start_month = week[5:8]
            start_date = int(week[9:11])
            end_month = week[-6:-3]
            end_date = int(week[-2:])
            if start_month == end_month:
                for i, date in enumerate(range(start_date, end_date + 1)):
                    data_date = f'{year} {start_month} {date}'
                    writer.writerow([data_date, values[i]])
            else:
                range_end = (4 - end_date) + start_date + 1
                for i, date in enumerate(range(start_date, range_end)):
                    data_date = f'{year} {start_month} {date}'
                    writer.writerow([data_date, values[i]])
                date = 1
                while date <= end_date:
                    index = date - (end_date + 1)
                    data_date = f'{year} {end_month} {date}'
                    writer.writerow([data_date, values[index]])
                    date = date + 1


def get_monthly_data(link):
    page = fetch_page(link)
    years = page.find_all(class_='B4')
    data_rows = [td.find_parent('tr') for td in years]

    with open(data_folder/'monthly.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Month', 'Price'])
        for data_row in data_rows:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            year, *values = [td.get_text() for td in data_row.find_all('td')]
            year = year.strip()
            values = [x if x != '' else '0.00' for x in values]
            for i, month in enumerate(months):
                writer.writerow([f'{year} {month} 1', values[i]])


def get_annual_data(link):
    page = fetch_page(link)
    decades = page.find_all(class_='B4')
    data_rows = [td.find_parent('tr') for td in decades]

    with open(data_folder/'annual.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Year', 'Price'])
        for data_row in data_rows:
            decade, *values = [td.get_text() for td in data_row.find_all('td')]
            decade = decade.strip()[:-3]
            values = [x if x != '' else '0.00' for x in values]
            for i, price in enumerate(values):
                writer.writerow([f'{decade}{i}', price])


if __name__ == '__main__':
    soup = fetch_page('rngwhhdm.htm')

    links = [a['href']
             for a in soup.find_all(class_='NavChunk')]

    get_daily_data(links[0])
    get_monthly_data(links[2])
    get_annual_data(links[3])

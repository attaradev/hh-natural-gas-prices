import requests
import csv
from bs4 import BeautifulSoup
from pathlib import Path

data_folder = Path(__file__).parent / '../data/'


def write_csv(file_name, data):
    """
    Writes a data to csv file
    """
    with open(data_folder / file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def isFloat(value):
    """
    Returns True when a value can be cast as float else return False
    """
    try:
        float(value)
        return True
    except:
        return False


def fetch_page(url):
    """
    Fetches and return a soup instance of a page for the provided partial url
    """
    base_url = 'https://www.eia.gov/dnav/ng/hist/'
    response = requests.get(base_url + url)
    return BeautifulSoup(response.content, 'html.parser')


def get_daily_data(link):
    """
    Writes daily gas prices to a csv
    """
    page = fetch_page(link)
    dates = page.find_all(class_='B6')
    data_rows = [td.find_parent('tr') for td in dates]

    with open(data_folder/'daily.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Price'])
        for data_row in data_rows:
            [week, *values] = [td.get_text().strip()
                               for td in data_row.find_all('td')]
            values = [x if isFloat(x) else 0.00 for x in values]
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
                if end_month == 'Jan':
                    year = int(year) + 1
                while date <= end_date:
                    index = date - (end_date + 1)
                    data_date = f'{year} {end_month} {date}'
                    writer.writerow([data_date, values[index]])
                    date = date + 1


def get_monthly_data(link):
    """
    Writes monthly gas prices to a csv
    """
    page = fetch_page(link)
    years = page.find_all(class_='B4')
    data_rows = [td.find_parent('tr') for td in years]

    with open(data_folder/'monthly.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Month', 'Price'])
        for data_row in data_rows:
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            [year, *values] = [td.get_text().strip()
                               for td in data_row.find_all('td')]
            values = [x if isFloat(x) else 0.00 for x in values]
            for i, month in enumerate(months):
                writer.writerow([f'{year} {month} 1', values[i]])


def get_annual_data(link):
    """
    Writes annual gas prices to a csv
    """
    page = fetch_page(link)
    decades = page.find_all(class_='B4')
    data_rows = [td.find_parent('tr') for td in decades]

    with open(data_folder/'annual.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Year', 'Price'])
        for data_row in data_rows:
            [decade, *
                values] = [td.get_text().strip()
                           for td in data_row.find_all('td')]
            decade = decade[:-3]
            values = [x if isFloat(x) else 0.00 for x in values]
            for i, price in enumerate(values):
                writer.writerow([f'{decade}{i}', price])


def get_weekly_data(link):
    """
    Writes weekly gas prices to a csv
    """
    page = fetch_page(link)
    month = page.find_all(class_='B6')
    data_rows = [td.find_parent('tr') for td in month]

    with open(data_folder/'weekly.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Week Ending', 'Price'])
        for data_row in data_rows:
            [month, week_1_end_date, week_1_value, week_2_end_date, week_2_value, week_3_end_date, week_3_value, week_4_end_date, week_4_value, week_5_end_date, week_5_value] = [
                td.get_text().strip() for td in data_row.find_all('td')]
            [year, mon] = month.split('-')

            values = [(week_1_end_date, week_1_value), (week_2_end_date, week_2_value),
                      (week_3_end_date, week_3_value), (week_4_end_date, week_4_value), (week_5_end_date, week_5_value)]
            values = [(v[0][-2:], v[1])
                      for v in values if v[0] != '']
            for data in values:
                writer.writerow([f'{year} {mon} {data[0]}', data[1]])


if __name__ == '__main__':
    soup = fetch_page('rngwhhdm.htm')

    links = [a['href']
             for a in soup.find_all(class_='NavChunk')]

    get_daily_data(links[0])
    get_weekly_data(links[1])
    get_monthly_data(links[2])
    get_annual_data(links[3])

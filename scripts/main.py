import csv
from pathlib import Path
import requests
from bs4 import BeautifulSoup

DATA_FOLDER = Path(__file__).parent / '../data/'


def write_csv(file_name, data):
    """
    Writes a data to csv file
    """
    with open(DATA_FOLDER / file_name, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)


def is_float(value):
    """
    Returns True when a value can be cast as float else return False
    """
    try:
        float(value)
        return True
    except ValueError:
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
    Get daily gas prices from link
    """
    daily_data = [['Date', 'Price']]
    page = fetch_page(link)
    dates = page.find_all(class_='B6')
    data_rows = [td.find_parent('tr') for td in dates]

    for data_row in data_rows:
        [week, *values] = [td.get_text().strip()
                           for td in data_row.find_all('td')]
        values = [x if is_float(x) else 0.00 for x in values]
        year = week[:4]
        start_month = week[5:8]
        start_date = int(week[9:11])
        end_month = week[-6:-3]
        end_date = int(week[-2:])
        if start_month == end_month:
            for i, date in enumerate(range(start_date, end_date + 1)):
                data_date = f'{year} {start_month} {date}'
                daily_data.append([data_date, values[i]])
        else:
            range_end = (4 - end_date) + start_date + 1
            for i, date in enumerate(range(start_date, range_end)):
                data_date = f'{year} {start_month} {date}'
                daily_data.append([data_date, values[i]])

            date = 1
            if end_month == 'Jan':
                year = int(year) + 1
            while date <= end_date:
                index = date - (end_date + 1)
                data_date = f'{year} {end_month} {date}'
                daily_data.append([data_date, values[index]])
                date = date + 1

    return daily_data


def get_monthly_data(link):
    """
    Get monthly gas prices from link
    """
    monthly_data = [['Month', 'Price']]
    page = fetch_page(link)
    years = page.find_all(class_='B4')
    data_rows = [td.find_parent('tr') for td in years]

    for data_row in data_rows:
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        [year, *values] = [td.get_text().strip()
                           for td in data_row.find_all('td')]
        values = [x if is_float(x) else 0.00 for x in values]

        for i, month in enumerate(months):
            monthly_data.append([f'{year} {month} 1', values[i]])

    return monthly_data


def get_annual_data(link):
    """
    Get annual gas prices from link
    """
    annual_data = [['Year', 'Price']]
    page = fetch_page(link)
    decades = page.find_all(class_='B4')
    data_rows = [td.find_parent('tr') for td in decades]

    for data_row in data_rows:
        [decade, *
         values] = [td.get_text().strip()
                    for td in data_row.find_all('td')]
        decade = decade[:-3]
        values = [x if is_float(x) else 0.00 for x in values]

        for i, price in enumerate(values):
            annual_data.append([f'{decade}{i}', price])

    return annual_data


def get_weekly_data(link):
    """
    Get weekly gas prices from link
    """
    weekly_data = [['Week Ending', 'Price']]
    page = fetch_page(link)
    month = page.find_all(class_='B6')
    data_rows = [td.find_parent('tr') for td in month]

    for data_row in data_rows:
        [month, week_1_end_date, week_1_value, week_2_end_date, week_2_value, week_3_end_date, week_3_value, week_4_end_date, week_4_value, week_5_end_date, week_5_value] = [
            td.get_text().strip() for td in data_row.find_all('td')]
        [year, mon] = month.split('-')

        values = [(week_1_end_date, week_1_value), (week_2_end_date, week_2_value),
                  (week_3_end_date, week_3_value), (week_4_end_date, week_4_value), (week_5_end_date, week_5_value)]
        values = [(v[0][-2:], v[1])
                  for v in values if v[0] != '']

        for data in values:
            weekly_data.append([f'{year} {mon} {data[0]}', data[1]])

    return weekly_data


if __name__ == '__main__':
    SOUP = fetch_page('rngwhhdm.htm')

    LINKS = [a['href']
             for a in SOUP.find_all(class_='NavChunk')]

    write_csv('daily.csv', get_daily_data(LINKS[0]))
    write_csv('weekly.csv', get_weekly_data(LINKS[1]))
    write_csv('monthly.csv', get_monthly_data(LINKS[2]))
    write_csv('annual.csv', get_annual_data(LINKS[3]))

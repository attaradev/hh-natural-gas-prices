from bs4 import BeautifulSoup
import os
import requests

base_url = 'https://www.eia.gov/dnav/ng/hist/'
response = requests.get(base_url + 'rngwhhdm.htm')

soup = BeautifulSoup(response.content, 'html.parser')

info = [(a.get_text().lower(), a['href'])
        for a in soup.find_all(class_='NavChunk')]

pages = [requests.get(base_url + i[1]).content for i in info]

for page in pages:
    print(page.prettify())

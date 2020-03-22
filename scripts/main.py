from bs4 import BeautifulSoup
import os
import requests


def fetch_page(url):
    base_url = 'https://www.eia.gov/dnav/ng/hist/'
    response = requests.get(base_url + url)
    return BeautifulSoup(response.content, 'html.parser')


soup = fetch_page('rngwhhdm.htm')

links = [(a.get_text().lower(), a['href'])
         for a in soup.find_all(class_='NavChunk')]

pages = [fetch_page(link[1]) for link in links]

print(pages[0].prettify())

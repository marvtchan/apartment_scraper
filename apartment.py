# apartment.py

from requests import get

response = get('https://sfbay.craigslist.org/search/eby/hhh?sort=rel&availabilityMode=0&sale_date=all+dates')

from bs4 import BeautifulSoup
html_soup = BeautifulSoup(response.text, 'html.parser')

posts = html_soup.find_all('li', class_= 'result-row')

print(type(posts))
print(len(posts))

print(posts[105])
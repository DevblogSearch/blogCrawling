import requests
from bs4 import BeautifulSoup
import json
import os

req = requests.get('https://github.com/sarojaba/awesome-devblog')

html = req.text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

soup = BeautifulSoup(html, 'html.parser')

table_data = soup.select(
    '#readme > div.Box-body.p-6 > article > table > tbody > tr > td'
)


blog_list = []

i = 0
while i < len(table_data):
    d = {}
    d['name'] = table_data[i].text
    d['link'] = table_data[i+1].find('a').get('href')
    d['desc'] = table_data[i+2].text
    d['social'] = table_data[i+1].find('a').get('href')
    blog_list.append(d)
    i += 4



with open(os.path.join(BASE_DIR, 'blog_list.json'), 'w+', encoding="utf-8") as json_file:
    json.dump(blog_list, json_file, ensure_ascii=False)




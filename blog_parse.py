import requests
from bs4 import BeautifulSoup
import json
import os
import articleDateExtractor

blog_data = []
blog_content = []
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def parse(i):
    req = requests.get(i['url'])
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')
    d = {}
    d['id'] = str(i['id'])
    d['blog'] = str(i['blog'])
    d['url'] = str(i['url'])
    d['title'] = str(soup.title.text)
    d['content'] = str(soup.body.text)
    d["creationDate"] = str(articleDateExtractor.extractArticlePublishedDate(i['url']))
    d["creationDate"] = d["creationDate"][:10]
    blog_content.append(d)


with open(os.path.join(BASE_DIR, 'blog_list.json'),'r', encoding='utf-8') as json_file:
    blog_data = json.load(json_file)

for i in blog_data:
    parse(i)

with open(os.path.join(BASE_DIR, 'blog_content.json'), 'w+', encoding="utf-8") as json_file:
    json.dump(blog_content, json_file, ensure_ascii=False)


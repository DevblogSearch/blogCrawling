from bs4 import BeautifulSoup
import requests
import json
import os
#import articleDateExtractor

blog_data = []
blog_content = []
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUFFER_SIZE = 10
DOC_UPDATE_URL = "http://127.0.0.1:80/document"

def parse_content(base_url, page_url, html):
    soup = BeautifulSoup(html, 'html.parser')
    d = {}
#    d['id'] = str(i['id'])
    d['blog'] = base_url
    d['url'] = page_url
    d['title'] = str(soup.title.text)
    d['content'] = str(soup.body.text)
#    d["creationDate"] = str(articleDateExtractor.extractArticlePublishedDate(i['url']))
#    d["creationDate"] = d["creationDate"][:10]
    buffered_document_send(d)

def buffered_document_send(data):
    headers = {'Content-Type': 'application/json', 'Accept':'application/json', 'charset':'utf-8'}
    res = requests.post(DOC_UPDATE_URL, headers=headers, json=[data])


from bs4 import BeautifulSoup
import requests
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUFFER_SIZE = 10
DOC_UPDATE_URL = "http://127.0.0.1:3000/document"

def naver_parse(soup):
    naver_content = ''
    if soup.find('div', {'id': 'postViewArea'}) == None:
        data = soup.findAll('div', {'class': 'se_textView'})
        TF = 1
        for content in data:
            if (TF):
                TF = 0
            elif (content.text != '\n\n'):
                naver_content += content.text
    else:
        naver_content = soup.find('div', {'id': 'postViewArea'}).text

    return naver_content

def tistory_parse(soup):
    tistory_content = ''
    if soup.find('div', {'class':'article'}) == None:
        tistory_content = soup.find('div', {'class': 'area_view'}).text
    else:
        tistory_content = soup.find('div', {'class':'article'}).text

    return tistory_content

def blogspot_parse(soup):
    blogspot_content = ''
    if soup.find('div', {'class':['article-content', 'entry-content']}) == None:
        blogspot_content = soup.find('div', {'class':['post-body', 'entry-content']}).text
    else:
        blogspot_content = soup.find('div', {'class':['article-content', 'entry-content']}).text
    return blogspot_content

def wordpress_parse(soup):
    wordpress_content = ''
    if soup.find('div', {'class':'entry-content'}) == None:
        if soup.find('div', {'id':'single'}) == None:
            if soup.find('div', {'class':'block-text'}) == None:
                wordpress_content = soup.find('div',{'class':'entry'}).text
            else:
                wordpress_content = soup.find('div',{'class':'block-text'}).text
        else:
            wordpress_content = soup.find('div', {'id':'single'}).text
    else:
        wordpress_content = soup.find('div', {'class':'entry-content'})
    return wordpress_content

def medium_parse(soup):
    medium_content = ''
    medium_content = soup.find('div',{'class':'postArticle-content'}).text
    return medium_content


def brunch_parse(soup):
    brunch_content = ''
    data = soup.findAll('div', {'class': 'wrap_body'})
    for content in data:
        brunch_content += content.text
    return brunch_content

def parse_content(base_url, page_url, html):
    soup = BeautifulSoup(html, 'html.parser')
    d = {}
    d['blog'] = base_url
    d['url'] = page_url
    d['title'] = soup.title.text
    if(base_url == 'blog.naver.com/'):
        d['content'] = naver_parse(soup)
    elif(base_url == 'tistory.com/'):
        d['content'] = tistory_parse(soup)
    elif(base_url == 'blogspot.com/'):
        d['content'] = blogspot_parse(soup)
    elif(base_url == 'wordpress.com/'):
        d['content'] = wordpress_parse(soup)
    elif(base_url == 'brunch.co.kr/'):
        d['content'] = brunch_parse(soup)
    elif(base_url == 'medium.com/'):
        d['content'] = medium_parse(soup)
    else:
        d['content'] = soup.body.text
        
    buffered_document_send(d)

def buffered_document_send(data):
    headers = {'Content-Type': 'application/json', 'Accept':'application/json', 'charset':'utf-8'}
    res = requests.post(DOC_UPDATE_URL, headers=headers, json=[data])

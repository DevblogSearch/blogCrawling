from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from html.parser import HTMLParser
from urllib import parse
from domain import *
from general import *
import blog_parse
import itertools
import requests
from threading import Lock

class Spider:

    project_name = ''
    base_url = ''
    domain_name = ''
    user_id = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()
    article_counter = dict()
    lock = Lock()

    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        #Spider.queue_file = './queue.txt'
        #Spider.crawled_file = './crawled.txt'
        Spider.queue.add(Spider.base_url)
        Spider.article_counter[base_url] = 1
        Spider.queue_file = "./data/" + Spider.project_name + '/queue.txt'
        Spider.crawled_file = "./data/" + Spider.project_name + '/crawled.txt'
        self.boot()
        Spider.queue.add(base_url)
        

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_dir('./data/' + Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    # Get Blogger's unique attribute in page url
    @staticmethod
    def get_blogger_ID(page_url):
        id = urlparse(page_url).path.replace("/", "")
        return id

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
        
        if page_url not in Spider.crawled:

            if page_url.find('medium.com') != -1:
                Spider.queue.remove(page_url)
                Spider.update_files()
                return

            # blog.naver.com // brunch.co.kr 전용 크롤링
            Spider.user_id = Spider.get_blogger_ID(Spider.base_url)
            if Spider.user_id != '':
                Spider.find_links_in_linear(page_url, Spider.user_id, 0)

            # 그 외 블로그 크롤링 시 사용하는 코드
            print(thread_name + ' now crawling ' + page_url)
            print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
            Spider.add_links_to_queue(Spider.gather_links(Spider.base_url, page_url))
            Spider.crawled.add(page_url)
        if page_url in Spider.queue:
            Spider.queue.remove(page_url)
        Spider.update_files()
            

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(base_url, page_url):

        page_links = set()
        try:
            req = Request(page_url, headers={'User-Agent' : 'Mozilla/5.0'})
            reqed = urlopen(req, timeout=3)
            if reqed.info().get_content_type() != 'text/html':
                return set()
            data = reqed.read()
            soup = BeautifulSoup(data, 'html.parser')
            res = soup.find_all('a', href = True)

            for link in res:
                url = parse.urljoin(base_url, link.get('href'))
                page_links.add(url)
            blog_parse.parse_content(base_url, page_url, data)

        except Exception as e:
            print(str(e))
            return set()

        return page_links
    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):

        is_same_domain = True    
        for url in links:
            if Spider.is_anchor_link(url):
                continue
            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            domname = get_domain_name(url)
            if domname.find(Spider.domain_name) == -1:
                is_same_domain = False
                break
            #for i in range(len(domname)):
            #    if len(Spider.domain_name) > len(domname):
            #        is_same_domain = False
            #        break
            #        
            #    if Spider.domain_name[i] != domname[i]:
            #        is_same_domain = False
            #        break

            if(is_same_domain):
                Spider.lock.acquire()
                try:
                    if Spider.article_counter[Spider.base_url] > 200:
                        break
                    Spider.article_counter[Spider.base_url] += 1
                finally:
                    Spider.lock.release() 
                Spider.queue.add(url)
            else: is_same_domain = True

    @staticmethod
    def find_links_in_linear(base_url, userid, num):
        return
        bidx = -1
        if base_url.find('naver.com') != -1:
            bidx = 0
        else:
            return

        if userid == 'blog':
            return
        URL_FORMAT = [
            "http://blog.naver.com/PostList.nhn?blogId={blog_id}&currentPage={page}"
            , "http://brunch.co.kr/{blog_Id}/{page}" ]

        #Blog_platform = URL_FORMAT[num]
        Blog_platform = URL_FORMAT[bidx]
        size_of_block = 0
        # itertools 이용, page의 값을 1부터 준다.
        for page in itertools.count(start=1):
            url = Blog_platform.format(blog_id = userid, page = page)

            # 요청을 보낸 뒤, 페이지가 없을 경우 iteration을 종료한다.
            try:
                r = requests.get(url)
                r.raise_for_status()
                print("Now Crawling : " + url)
            except requests.HTTPError as e:
                print(e)
                break

            # URL만 얻어온 후, crawled 된 페이지 + 1
            Spider.crawled.add(url)
            size_of_block += 1
            
            # if crawler gathers 50 links in the queue, update crawled.txt file.
            Spider.update_files()
            size_of_block = 0
    
    @staticmethod
    def is_anchor_link(url):
        if url.split('/')[-1].find('#') == 0:
            return True
        return False
    

    @staticmethod
    def update_files():
        Spider.lock.acquire()
        try:
            set_to_file(Spider.queue, Spider.queue_file)
            set_to_file(Spider.crawled, Spider.crawled_file)
        finally:
            Spider.lock.release()

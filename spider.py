from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from urllib import parse
from domain import *
from general import *
from selenium import webdriver
import requests
import time


class Spider:
    project_name = ''
    base_url = ''
    domain_name = ''
    user_id = ''
    queue_file = ''
    crawled_file = ''
    queue = set()
    crawled = set()

    def __init__(self, project_name, base_url, domain_name):
        Spider.project_name = project_name
        Spider.base_url = base_url
        Spider.domain_name = domain_name
        Spider.queue_file = Spider.project_name + '/queue.txt'
        Spider.crawled_file = Spider.project_name + '/crawled.txt'
        self.boot()
        self.crawl_page('First spider', Spider.base_url)

    # Creates directory and files for project on first run and starts the spider
    @staticmethod
    def boot():
        create_project_dir(Spider.project_name)
        create_data_files(Spider.project_name, Spider.base_url)
        Spider.queue = file_to_set(Spider.queue_file)
        Spider.crawled = file_to_set(Spider.crawled_file)

    # Get Blogger's unique attribute in page url (only can use on naver blog)
    @staticmethod
    def get_blogger_ID(page_url):
        id = urlparse(page_url).path.replace("/", "")
        return id

    # Updates user display, fills queue and updates files
    @staticmethod
    def crawl_page(thread_name, page_url):
            Pdomain_name = get_sub_domain_name(page_url).split('.')

            # medium 블로그 크롤링 시 이용
            if Pdomain_name[-2] == "medium":
                path = "C:\\Users\\rhyme\\Downloads\\chromedriver_win32\\chromedriver.exe"

                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--window-size=1920x1080')
                options.add_argument('--disable-gpu')

                driver = webdriver.Chrome(executable_path=path, options = options)
                Spider.add_links_in_medium(Spider.gather_links_in_medium(Spider.base_url, driver))

                driver.close()

                Spider.queue.remove(page_url)
                Spider.crawled.add(page_url)
                Spider.update_files()

            # db.yml 파일 사용 시 주석처리 해줘야 함.
            elif Pdomain_name[-2] == "blogspot":
                path = "C:\\Users\\rhyme\\Downloads\\chromedriver_win32\\chromedriver.exe"

                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--window-size=1920x1080')
                options.add_argument('--disable-gpu')


                driver = webdriver.Chrome(executable_path=path, options=options)
                Spider.add_links_in_sync_web(Spider.gather_links_in_sync_web(page_url, driver))

                driver.close()
                Spider.queue.remove(page_url)
                Spider.crawled.add(page_url)
                Spider.update_files()

            # blog.naver.com // brunch.co.kr 전용 크롤링
            # naver 일 때, linear함수의 int 인자값으로 0, brunch 일 때, 인자값으로 1 입력
            elif (len(Pdomain_name) > 2 and
                  (Pdomain_name[-3] == "brunch" or Pdomain_name[-2] == "naver")):

                idx = 0
                if (Pdomain_name[-3] == "brunch"): idx = 1

                Spider.user_id = Spider.get_blogger_ID(Spider.base_url)
                Spider.find_links_in_linear(page_url, Spider.user_id, idx)
                Spider.queue.remove(page_url)
                Spider.update_files()

            # 그 외 블로그 크롤링 시 사용하는 코드
            else:
                # print(thread_name + ' now crawling ' + page_url)
                # print('Queue ' + str(len(Spider.queue)) + ' | Crawled  ' + str(len(Spider.crawled)))
                Spider.add_links_to_queue(Spider.gather_links(Spider.base_url, page_url))
                Spider.queue.remove(page_url)
                Spider.crawled.add(page_url)
                Spider.update_files()

    # Converts raw response data into readable information and checks for proper html formatting
    @staticmethod
    def gather_links(base_url, page_url):

        page_links = set()
        try:
            req = Request(page_url, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(urlopen(req), 'html.parser')
            res = soup.find_all('a', href=True)

            for link in res:
                url = parse.urljoin(base_url, link.get('href'))
                page_links.add(url)
        except Exception as e:
            print(str(e))
            return set()

        print(page_links)
        return page_links

    # Saves queue data to project files
    @staticmethod
    def add_links_to_queue(links):

        is_same_domain = True
        for url in links:
            print("Now Crawling : " + url)

            if (url in Spider.queue) or (url in Spider.crawled):
                continue
            if (url.find("https") == 0):
                url = url.replace("https", "http")

            for i in range(len(Spider.base_url) - 1):
                if Spider.domain_name[i] != get_domain_name(url)[i]:
                    is_same_domain = False
                    break

            if (is_same_domain):
                Spider.queue.add(url)
            else:
                is_same_domain = True

    @staticmethod
    def find_links_in_linear(base_url, userid, num):

        URL_FORMAT = ["http://blog.naver.com/PostList.nhn?blogId={blog_id}&currentPage={page}"
            , "http://brunch.co.kr/{blog_id}/{page}"]
        Blog_platform = URL_FORMAT[num]
        size_of_block = 0

        # 브런치 블로그 크롤링 , num = 1
        # 요청을 보낸 뒤, 페이지가 없을 경우 iteration을 종료한다.
        if num == 1:
            for page in itertools.count(start=1):
                url = Blog_platform.format(blog_id=userid, page=page)

                try:
                    r = requests.get(url)
                    r.raise_for_status()
                except requests.HTTPError as e:
                    print(e)
                    break
                print("Now Crawling : " + url)
                Spider.crawled.add(url)
                size_of_block += 1
                if (size_of_block >= 10):
                    Spider.update_files()
                    size_of_block = 0

        else:
            # 네이버 블로그 리디렉션
            page = 1

            # page를 1부터 증가시켜 100개의 page만 확인한다.
            while (page < 101):
                url = Blog_platform.format(blog_id=userid, page=page)

                r = requests.get(url)
                soup = BeautifulSoup(r.text, 'html.parser')

                redirected_url = soup.find_all('a', {'class': 'fil5 pcol2'})
                redirected_url += soup.find_all('a', {
                    'class': "url pcol2 _setClipboard _returnFalse _se3copybtn _transPosition"})

                redirection_url_format = "https://blog.naver.com/PostView.nhn?blogId={blogid}&logNo={log_No}&categoryNo=0&parentCategoryNo=0&viewDate=&currentPage=1&postListTopCurrentPage=1&from=menu"

                try:
                    print("Now Crawling : " + url)
                    for i in range(0, len(redirected_url)):
                        if (redirected_url[i].get('class') == 'fil5 pcol2'
                                or redirected_url[i].get('class')[0] == 'fil5'):

                            real_url = redirected_url[i].get('href')
                            logNo = urlparse(real_url).path.replace("/", "")[len(userid):]
                            Spider.crawled.add(redirection_url_format.format(blogid=userid, log_No=logNo))
                        else:
                            real_url = redirected_url[i].get('title')
                            logNo = urlparse(real_url).path.replace("/", "")[len(userid):]
                            Spider.crawled.add(redirection_url_format.format(blogid=userid, log_No=logNo))
                        # crawled.txt에 url 추가 후 size_of_block +1
                        size_of_block += 1

                    # if crawler gathers 50 links in the queue, update crawled.txt file.
                    if (size_of_block >= 10):
                        Spider.update_files()
                        size_of_block = 0

                    page += 1
                except Exception as e:
                    print("error발생 : " + e)
                    break

        # 추가되지않고 남아있는 url을 모두 update해준다.
        Spider.update_files()

    # blogspot 동적 페이지 용 크롤러
    @staticmethod
    def add_links_in_sync_web(links):
        is_same_domain = True
        try:
            for url in links:
                if (url in Spider.queue) or (url in Spider.crawled):
                    continue

                print("Crawl : " + url)
                # .com, .kr이 다르더라도 id, platform이 같은 경우는
                # 같은 블로그의 글로 취급한다.
                for i in range(len(Spider.base_url) - 3):
                    if Spider.domain_name[i] != get_domain_name(url)[i]:
                        is_same_domain = False
                        break

                if (is_same_domain): Spider.queue.add(url)
                else: is_same_domain = True
        except Exception as e:
            print(str(e))
            return
    @staticmethod
    def gather_links_in_sync_web(page_url, driver):
        page_links = set()
        openurl = "window.open('{url}');"
        openurl = openurl.format(url=page_url)


        try:
            driver.execute_script(openurl)
            driver.switch_to.window(driver.window_handles[-1])
            raw_links = driver.find_elements_by_xpath("//a[@href]")
            for link in raw_links:
                href = link.get_attribute("href")
                if (href.count("/") >4 and href[-1] != "/"):
                    page_links.add(href)

        except Exception as e:
            print(str(e))
            return set()

        return page_links

    @staticmethod
    def add_links_in_medium(links):
        for url in links:
            Spider.crawled.add(url)

    # medium 페이지 용 크롤러 (도메인 판별)
    @staticmethod
    def gather_links_in_medium(base_url, driver):
        page_links = set()
        openurl = "window.open('{url}');"
        openurl = openurl.format(url=base_url)

        try:
            driver.execute_script(openurl)
            driver.switch_to.window(driver.window_handles[-1])

            lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            match = False
            while (match == False):
                lastCount = lenOfPage
                time.sleep(3)
                lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
                if lastCount == lenOfPage: match = True

            raw_links = driver.find_elements_by_xpath("//a[@href]")
            for link in raw_links:
                href = link.get_attribute("href")
                if (href.find('/p/') != -1):
                    href = base_url + "/" + href[href.find('/p/')+ 3: href.find('?')]
                    print("Crawl : " + href)
                    page_links.add(href)

        except Exception as e:
            print(str(e))
            return set()
        return page_links

    @staticmethod
    def update_files():
        set_to_file(Spider.queue, Spider.queue_file)
        set_to_file(Spider.crawled, Spider.crawled_file)

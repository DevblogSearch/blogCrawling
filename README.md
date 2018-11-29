# blogCrawling

*Spider 원본 Source*

<https://github.com/buckyroberts/Spider>

*유튜브로 소스 설명해줌.*

<https://www.youtube.com/watch?v=nRW90GASSXE&list=PL6gx4Cwl9DGA8Vys-f48mAH9OKSUyav0q>

*Beautiful soup, Selenium 공부자료.*

<https://beomi.github.io/gb-crawling/posts/2017-01-20-HowToMakeWebCrawler.html>

*한글화 된 문서*

<http://creativeworks.tistory.com/entry/Web-Crawler-001-Creating-a-New-Project?category=638090>


# Overview

한국 개발자 블로그 웹사이트의 크롤러 부분입니다.

블로그는 https://github.com/sarojaba/awesome-devblog 의 db.yml 파일에서 데이터를 얻어오고 있습니다.


# 소스 파일 설명

*spider.py

크롤러의 실제적인 부분입니다. 블로그 url을 얻어 txt파일로 저장합니다.

URL을 parse_content.py에 보내줍니다.

*domain.py

url의 도메인 부분(netloc)만 얻을 때 이용합니다.

*general.py

얻어온 url을 저장할 디렉토리와 txt파일을 만들 때 이용합니다.

*blog_parse.py

spider.py에서 넘겨준 url에 request를 보내

글 내용을 beautifulsoup로 가져와 딕셔너리 타입으로 저장합니다.

이후 서버에 json 형태로 보내주는 파일입니다.


# 기본 설정

selenium, beautifulsoup 이용

pip selenium package

pip install selenium

BeautifulSoup은 pip install bs4로 설치

Google Chrome, Chrome driver 설치 (선택)


# 이용 방법

main.py에서 원하는 블로그 플랫폼이 저장된 yml 파일을 입력 값으로 넣어줍니다.

사용한 yml 파일에 따라 main.py에 있는 NUM_OF_BLOGGERS 값을 변경해줍니다.

다른 url에서 이용하기 위해서는 yml 파일에 있는 형식으로 url과 name을 추가하면 가능합니다.

chrome webdriver 설치 후 (설치 : https://sites.google.com/a/chromium.org/chromedriver/downloads)

spider.py의 path = "webdriver가 설치된 위치" 를 변경해주면 동적 blog(blogspot, medium) 또한 크롤링 가능합니다.

※ db.yml 파일 사용 시 주석처리 해줘야 함. (spider.py)

        elif Pdomain_name[-2] == "blogspot":
            path = "C:\\Users\\rhyme\\Downloads\\chromedriver_win32\\chromedriver.exe"

            options = webdriver.ChromeOptions()
            options.add_argument("--headless")

            driver = webdriver.Chrome(executable_path = path, chrome_options = options)
            Spider.add_links_in_sync_web(Spider.gather_links_in_sync_web(page_url, driver))

            driver.close()
            Spider.queue.remove(page_url)
            Spider.crawled.add(page_url)
            Spider.update_files()

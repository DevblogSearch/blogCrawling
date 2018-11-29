import threading
import yaml
from spider import Spider
from domain import *
from general import *
import sys, os

stream = open('test.yml', 'r', encoding="UTF8")
data = yaml.load(stream)
NUMBER_OF_THREADS = 1
# db.yml = 1053 // db_sync_blogspot = 3
NUMBER_OF_BLOGGERS = 3

for person in range(NUMBER_OF_BLOGGERS):
    try:
        if 'name' not in data[person] or 'blog' not in data[person]:
            continue

        PROJECT_NAME = data[person]['name']
        HOMEPAGE = data[person]['blog']
        DOMAIN_NAME = data[person]['blog']
        Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)

        QUEUE_FILE = os.path.join('user' , PROJECT_NAME , 'queue.txt')
        CRAWLED_FILE = os.path.join('user' , PROJECT_NAME , 'crawled.txt')

        while True:
            queued_links = file_to_set(QUEUE_FILE)
            if len(queued_links) == 0:
                break

            for link in queued_links:
                Spider.crawl_page(threading.current_thread().name, link)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))

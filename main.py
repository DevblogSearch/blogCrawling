import threading
import yaml
from random import shuffle
from time import sleep
from queue import Queue
from spider import Spider
from domain import *
from general import *

stream = open('db.yml', 'r', encoding = "UTF8")
data = yaml.load(stream)
shuffle(data)
print(len(data))

NUMBER_OF_THREADS = 1

# get num of bloggers in db.yml by using tag 'name'
NUMBER_OF_BLOGGERS = len(data) # for test (original value : 1053)

# Create worker threads (will die when main exits)
def create_workers():
    for _ in range(NUMBER_OF_THREADS):
        t = threading.Thread(target=work)
        t.daemon = True
        t.start()


# Do the next job in the queue
def work():
    while True:
        url = queue.get()
        Spider.crawl_page(threading.current_thread().name, url)
        queue.task_done()


# Each queued link is a new job
def create_jobs():
    for link in file_to_set(QUEUE_FILE):
        Spider.crawl_page('main', link)
    queue.join()


# Check if there are items in the queue, if so crawl them
def crawl():
    tmp = 0
    cnt = 0
    while True:
        queued_links = file_to_set(QUEUE_FILE)
        if len(queued_links) > 0:
            if tmp == len(queued_links):
                if cnt == 10:
                    print('passed')
                    break
                cnt +=1
            else:
                tmp = len(queued_links)
                cnt  = 0
            print(str(len(queued_links)) + ' links in the queue')
            create_jobs()
        else:
            break


for person in range(NUMBER_OF_BLOGGERS):
    if 'blog' not in data[person] or 'name' not in data[person]:
        continue
    HOMEPAGE = data[person]['blog']
    PROJECT_NAME = data[person]['name']
    if PROJECT_NAME.find('http://') != -1:
        PROJECT_NAME = PROJECT_NAME[7:]
    DOMAIN_NAME = get_domain_name(HOMEPAGE)
    Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)
    
    QUEUE_FILE = "./data/" + PROJECT_NAME + '/queue.txt'
    CRAWLED_FILE ="./data"+ PROJECT_NAME + '/crawled.txt'
    #QUEUE_FILE = './queue.txt'
    #CRAWLED_FILE = './crawled.txt'
    queue = Queue()
    
    crawl()
    

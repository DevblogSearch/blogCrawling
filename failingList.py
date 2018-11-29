
def write_list(BASE_DIR, base_url, page_url, e):
    f = open(BASE_DIR + '/Blog failing parse.txt', 'a')
    f.write('base_url: ' + base_url + ', page_url' + page_url + ', error: ' + e)
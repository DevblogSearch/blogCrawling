from urllib.parse import urlparse


# Get domain name (example.com)
def get_domain_name(url):
    try:
        return url
    except:
        return ''


# Get sub domain name (name.example.com)
def get_sub_domain_name(url):
    try:
        return urlparse(url).netloc
    except:
        return ''

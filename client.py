import threading
import requests
import time
from concurrent.futures import ThreadPoolExecutor

def post_data(uri, id):
    img_url = 'http://www.pyimagesearch.com/wp-content/uploads/2015/01/google_logo.png'
    payload = {'ts': time.time(), 'url' : img_url, 'id' : id}
    requests.post(uri, data = payload)

def main():
    endpoint = '/testB'
    url = 'http://120.92.114.24:8010'
    uri = url + endpoint

    threadnumber = 50000
    pool = ThreadPoolExecutor(threadnumber)

    
    for i in range(threadnumber):
        pool.submit(post_data, uri, i)

if __name__ == '__main__':
    main()
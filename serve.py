from flask import Flask, request
import Queue
from concurrent.futures import ThreadPoolExecutor
import requests
import threading
import numpy as np
import urllib
import cv2
import time

app = Flask(__name__)
request_queue = Queue.Queue()
MAX_EXECUTING_SIZE = 5000000
batchsize = 50000
executing_queue = Queue.Queue(MAX_EXECUTING_SIZE)
executor = ThreadPoolExecutor(batchsize)

@app.route('/')
def test_ok():
    return 'connect success'

@app.route('/testB', methods = ['POST'])
def testB():
    if request.method == 'POST':
        request_queue.put(request.form)
    return 'ok'

@app.route('/do', methods = ['POST'])
def do():
    if request.method == 'POST':
        if executing_queue.qsize() >= MAX_EXECUTING_SIZE:
            return 'executing_queue has been full fitted'
        if request_queue.qsize() == 0:
            return 'request_queue is empty'

        while executing_queue.qsize() < batchsize and request_queue.qsize() > 0:
            reqform = request_queue.get()
            executing_queue.put(reqform)

        return 'ok'

def consumer():
    while True:
        if executing_queue.qsize() < batchsize and request_queue.qsize() > 0:
            requests.post('http://127.0.0.1:8010/do')
        
        if executing_queue.qsize() == batchsize:
            print('begin to work')
            for i in range(batchsize):
                reqdata = executing_queue.get()
                executor.submit(work, reqdata)

def work(reqdata):
    dataform = reqdata.to_dict()
    rec_ts = float(dataform['ts'])

    img_url = dataform['url']
    resp = urllib.urlopen(img_url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    resp_ts = time.time()
    ts_diff = resp_ts - rec_ts
    feed_back = {'rec_ts': rec_ts, 'resp_ts' : resp_ts, 'ts_diff': ts_diff}
    print(feed_back)

    

if __name__ == '__main__':
    threading.Thread(target=consumer, ).start()

    app.run(host = '0.0.0.0',
            port = '8010')
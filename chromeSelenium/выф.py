from multiprocessing import Process
import threading
import os
import time

def start():
    for i in range(100):
        print('Привет')
        time.sleep(1)

def scraper(url):
    for i in range(100):
        print('ccылка')
        time.sleep(2)

t = threading.Thread(target=scraper, args=[111,])

t.start()
t1 = threading.Thread(target=start)
t1.start()

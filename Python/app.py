import requests
import re
import os
import time
import random
import threading
from bs4 import BeautifulSoup
from  proxy import ScrapeProxy

lock = threading.Lock()

def task(sp, i_list):
    global lock

    r = requests.session()
    for i in i_list:
        try:
            html = r.get("{}".format(i),  headers = sp.get_random_user_agent())
        except:
            if 'http' in r.proxies:
                r.proxies = { 'http': sp.get_random_ip(r.proxies['http']) }
            else:
                r.proxies = { 'http': sp.get_random_ip("") }
                
            html = r.get("{}".format(i),  headers = sp.get_random_user_agent())
        html.encoding = 'UTF-8'
        soup = BeautifulSoup(html.text, 'lxml')

        # Use BeautifulSoup to get data needed here.
        
        print(i)
        
        lock.acquire()
        # write DB or File here.
        lock.release()
    return []

if __name__ == "__main__":
    sp = ScrapeProxy(ip_num = 10)    
    sp.get_ip_list()
    
    start_time = time.time() 

    ths = []
    for i in range(1, 21, 20):
        th = threading.Thread(target = task,args = (sp, list(range(i, i+20))))
        th.start()
        ths.append(th)
    for th in ths:
        th.join()

    print("--- %s seconds ---" % (time.time() - start_time))






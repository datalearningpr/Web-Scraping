
import requests
import re
import random
import time
from bs4 import BeautifulSoup
from selenium import webdriver

class ScrapeProxy:
    def __init__(self, ip_filter = [], ip_num = 10, test_url = "https://en.wikipedia.org/wiki/Python",
        user_agent_file = "ChromeUserAgent.txt",
        phantomjs_path = "D:\\Program Files\\phantomjs-2.1.1-windows\\bin\\phantomjs.exe"):
        self.headers = {
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive'
        }
        f = open(user_agent_file, "r")
        self.user_agent_list = f.read().split("\n")
        f.close()
        self.proxy_url='https://free-proxy-list.net/'
        self.test_url = test_url
        self.ip_num = ip_num
        self.phantomjs_path = phantomjs_path
        self.ip_list = []
        self.ip_filter = ip_filter

    def test_ip(self, ip, set_timeout = 1):
        try:
            requests.get(self.test_url, headers = self.headers, proxies = { 'http': ip }, timeout = set_timeout)
            return True
        except:
            return False

    def get_proxy_html(self):
        driver = webdriver.PhantomJS(executable_path = self.phantomjs_path)
        driver.get(self.proxy_url)
        time.sleep(1)
        driver.execute_script("document.getElementsByName(\"proxylisttable_length\")[0].options[2].value='300'")
        driver.execute_script("$(\"select[name='proxylisttable_length']\").val('300').change()")
        time.sleep(0.5)
        html = driver.page_source
        driver.close()
        return html

    def get_ip_list(self):
        ip_list=[]
        proxy_html = self.get_proxy_html()
        proxy_bs = BeautifulSoup(proxy_html, 'lxml')
        for span in proxy_bs.findAll("tr", { "class": ["odd", "even"] }):
            temp = span.findAll("td")
            span_ip = "" + temp[0].text + ":" + temp[1].text
            if self.test_ip(span_ip) and span_ip not in self.ip_filter:
                ip_list.append(span_ip)
                print('test passed, ip is: ' + str(span_ip))
                if len(ip_list) >= self.ip_num:
                    print('Gathered ' + str(len(ip_list)) + ' valid ip.')
                    break
        self.ip_list = ip_list

    def get_random_ip(self, input_ip = ""):
        l = self.ip_list.copy()
        if input_ip in l:
            l.remove(input)
        output = random.choice(l)
        return output

    def get_random_user_agent(self, input_user_agent = ""):
        l = self.user_agent_list.copy()
        if input_user_agent in l:
            l.remove(input)
        output = random.choice(l)
        headers = {
            'User-Agent': output,
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }
        return headers

if __name__ == "__main__":
    sp = ScrapeProxy()
    sp.get_ip_list()
    print(sp.get_random_ip())
    print(sp.get_random_user_agent())
    
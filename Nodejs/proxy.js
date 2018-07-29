const puppeteer = require('puppeteer');
const request = require('request-promise');
const fs = require('fs');

class ScrapeProxy {
  constructor(ip_num = 10, ip_filter = [], test_url = "https://en.wikipedia.org/wiki/Python",
              user_agent_file = "ChromeUserAgent.txt") {
    this.headers = {
      'Accept-Encoding': 'gzip, deflate, sdch',
      'Accept-Language': 'en-US,en;q=0.8',
      'Upgrade-Insecure-Requests': '1',
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Cache-Control': 'max-age=0',
      'Connection': 'keep-alive'
    };
    let f = fs.readFileSync(user_agent_file, 'utf8');
    this.user_agent_list = f.split("\n");
    this.proxy_url='https://free-proxy-list.net/';
    this.test_url = test_url;
    this.ip_num = ip_num;
    this.ip_list = [];
    this.ip_filter = ip_filter;
  }

  async testIP(ip, set_timeout = 1000) {
    let result = null;
    await request
      .get(this.test_url, { 
        timeout: set_timeout,
        headers: this.headers,
        proxy: ip,
      }).then(() => {
        result = true;
      }).catch((e) => {
        result = false;
      })
    return result;
  }

  async getIPList() {
    const browser = await puppeteer.launch({
      headless: true
    });
    const page = await browser.newPage();

    await page.goto('https://free-proxy-list.net/');
    const result = await page.evaluate(async () => {
      document.getElementsByName("proxylisttable_length")[0].options[2].value='300';
      $("select[name='proxylisttable_length']").val('300').change();

      let data = [];
      const trs = document.querySelectorAll("tr.odd, tr.even");
      for(let tr of trs) {
        tds = tr.getElementsByTagName("td");
        span_ip = `http://${tds[0].textContent}:${tds[1].textContent}`;
        data.push(span_ip);
      }
      return data;
    });
    browser.close();
    this.ip_list = [];
    for(let ip of result) {
      const isValid = await this.testIP(ip);
      if (isValid && !this.ip_filter.some(d => JSON.stringify(d) === JSON.stringify(ip))) {
        this.ip_list.push(ip);
        console.log('test passed, ip is: ' + JSON.stringify(ip));
        if (this.ip_list.length >= this.ip_num) {
          console.log('Gathered ' + this.ip_list.length + ' valid ip.')
          break;
        }
      }
    }
  }

  getRandomIP(inputIP = {}) {
    let sample = this.ip_list.filter(d => JSON.stringify(d) !== JSON.stringify(inputIP));
    return sample[Math.floor(Math.random() * sample.length)];
  }

  getRandomUserAgent(inputUserAgent = "") {
    let sample = this.user_agent_list.filter(d => d !== inputUserAgent);
    let headers = {
      'User-Agent': sample[Math.floor(Math.random() * sample.length)],
      'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    return headers
  }
}

module.exports = ScrapeProxy;

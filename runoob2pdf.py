import os
import re
import time
import datetime
import random
from urllib.parse import urlparse

import pdfkit
import requests
from bs4 import BeautifulSoup


htmlTemplate = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="http://www.runoob.com/wp-content/themes/runoob/style.css?v=1.12" type="text/css" media="all" />
</head>
<body>
{}
</body>
</html>
"""


class runoob2pdf(object):
    def __init__(self, startUrl):
        """
            :param startUrl: (e.g.,http://www.runoob.com/xml/xml-tutorial.html)
        """
        self.startUrl = startUrl
        self.domain = f'{urlparse(self.startUrl).scheme}://{urlparse(self.startUrl).netloc}'
        self.fileName = self.startUrl.split('/')[-1].split('.')[0]
        self.ipList = []
        self.userAgentList = [
            "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
            "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
            "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
            "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
            "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
            "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
            "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
            "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
            "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
            "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
        ]

    def getProxyIp(self):
        userAgent = random.choice(self.userAgentList)
        header = { 'User-Agent': userAgent }
        for i in range(2):
            try:
                url = f'http://www.xicidaili.com/wt/{i}'
                response = requests.get(url, headers=header)
                soup = BeautifulSoup(response.content, 'lxml')
                trs = soup.findAll('tr')
                for i in range(1, len(trs)):
                    tds = trs[i].findAll('td')
                    proxyIP = f'{tds[1].contents[0]}:{tds[2].contents[0]}'
                    yield proxyIP
            except:
                continue

    def validateIp(self, proxyIP, timeout=500):
        testUrl = 'https://www.baidu.com/'
        start = datetime.datetime.now()
        try:
            requests.get(testUrl, proxies={ 'http': proxyIP.strip() })
        except:
            print(f'抛弃IP:{proxyIP} \t 严重超时')
            return
        end = datetime.datetime.now()
        passed = int((end - start).total_seconds() * 1000)
        if passed > timeout:
            print(f'抛弃IP:{proxyIP} \t 验证时间:{passed}ms')
        else:
            print(f'可用IP:{proxyIP} \t 验证时间:{passed}ms')
            self.ipList.append(proxyIP)

    def crawl(self, url, proxy=None, retriesNum=3):
        userAgent = random.choice(self.userAgentList)
        header = { 'User-Agent': userAgent }
        if proxy == None:
            try:
                print(url)
                response = requests.get(url, headers=header)
                return response
            except:
                if retriesNum > 0:
                    print('获取网页失败，1s后将重新获取')
                    time.sleep(1)
                    return self.crawl(url, retriesNum-1)
                else:
                    print('开始使用代理')
                    IP = random.choice(self.ipList).strip()
                    proxy = { 'http': IP }
                    return self.crawl(url, proxy)
        else:
            try:
                response = requests.get(url, headers=header, proxies=proxy)
                return response
            except:
                if retriesNum > 0:
                    print('正在更换代理，1s后将重新获取')
                    time.sleep(1)
                    IP = random.choice(self.ipList).strip()
                    proxy = { 'http': IP }
                    print(f'当前代理是：{proxy}')
                    return self.crawl(url, proxy, retriesNum-1)
                else:
                    print('代理失败，取消代理')
                    return self.crawl(url, 3)

    def parseMenu(self, response):
        soup = BeautifulSoup(response.content, 'lxml')
        menu = soup.find_all(class_='design')
        for link in menu:
            links = link.find_all(href=True)
        for a in links:
            url = a.get("href")
            if not url.startswith("http"):
                url = "".join([self.domain, url])
            yield url

    def parseBody(self, response):
        soup = BeautifulSoup(response.content, 'lxml')
        html = str(soup.find_all(class_='article-body')[0])

        def func(m):
            if not m.group(2).startswith('http'):
                return ''.join([m.group(1), self.domain, m.group(2), m.group(3)])
            else:
                return ''.join([m.group(1), m.group(2), m.group(3)])
        pattern = re.compile('(<img .*?src=\")(.*?)(\")')
        return htmlTemplate.format(pattern.sub(func, html)).encode('utf-8')

    def main(self):
        for proxyIP in self.getProxyIp():
            self.validateIp(proxyIP)
        htmls = []
        for index, url in enumerate(self.parseMenu(self.crawl(self.startUrl))):
            content = self.parseBody(self.crawl(url))
            htmlName = '.'.join([str(index), 'html'])
            with open(htmlName, 'wb') as f:
                f.write(content)
            htmls.append(htmlName)
        pdfkit.from_file(htmls, self.fileName + '.pdf')
        for i in htmls:
            os.remove(i)


if __name__ == '__main__':
    print('输入起始地址：')
    startUrl = input()
    if startUrl:
        crawler = runoob2pdf(startUrl)
        crawler.main()

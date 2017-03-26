# -*- coding: UTF-8 -*-
import os
import re
import time
import random
import pdfkit
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse  
htmlTemplate = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
</head>
<body>
{content}
</body>
</html>
"""
class runoobToPDF(object):   
    def __init__(self, fileName, startUrl): 
        self.fileName = fileName
        self.startUrl = startUrl
        self.domain = '{uri.scheme}://{uri.netloc}'.format(uri=urlparse(self.startUrl))
        self.ipList=[]
        ipHTML=requests.get("http://haoip.cc/tiqu.htm")
        ips=re.findall(r'r/>(.*?)<b',ipHTML.text,re.S)
        for ip in ips:
            ip=re.sub("\n","",ip)    
            self.ipList.append(ip.strip())
        self.userAgentList=[
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
    def crawl(self, url,proxy=None,retriesNum=3):
        userAgent=random.choice(self.userAgentList)
        header={"User-Agent":userAgent}
        if proxy==None:
            try:
                print(url)
                response=requests.get(url,headers=header)
                return response
            except:
                if retriesNum>0:
                    time.sleep(1)
                    print("获取网页失败，1s后将重新获取")
                    return self.crawl(url,retriesNum-1)  
                else:
                    print("开始使用代理")
                    time.sleep(1)
                    IP="".join(str(random.choice(self.ipList)).strip())
                    proxy={"http":IP}
                    return self.crawl(url,proxy)
        else:
            try:
                print(url) 
                response=requests.get(url,headers=header,proxies=proxy)
                return response
            except:
                if retriesNum>0:
                    time.sleep(1)
                    IP="".join(str(random.choice(self.ipList)).strip())
                    proxy={"http":IP} 
                    print("正在更换代理，1s后将重新获取")
                    print("当前代理是：",proxy)
                    return self.crawl(url,proxy,retriesNum-1)
                else:
                    print("代理错误，取消代理")
                    return self.crawl(url,3)       
    def parseMenu(self, response):
        soup = BeautifulSoup(response.content, "lxml")
        menu = soup.find_all(class_="design")
        for link in menu:
            links = link.find_all(href=True) 
        for a in links:
            url = a.get("href")
            if not url.startswith("http"):
                url = "".join([self.domain, url]) 
            yield url
    def parseBody(self, response):
            soup = BeautifulSoup(response.content, 'lxml') 
            html = str(soup.find_all(class_="article-body"))
            html = htmlTemplate.format(content=html).encode("utf-8")
            return html          
    def main(self):
        startTime = time.time()
        options = {
        'quiet': ''
        }
        htmls = []
        for index, url in enumerate(self.parseMenu(self.crawl(self.startUrl))):
            html = self.parseBody(self.crawl(url))
            htmlName = ".".join([str(index), "html"])
            with open(htmlName, 'wb') as f:
                f.write(html)
            htmls.append(htmlName)
        pdfkit.from_file(htmls, self.fileName + ".pdf", options=options)
        for htmlName in htmls:
            os.remove(htmlName)
        totalTime = time.time() - startTime
        print("总共耗时：%f 秒" % totalTime)
if __name__ == '__main__':
    print("起始地址：")
    startUrl = input()
    print("保存文件名(不需要后缀名)：")
    fileName = input()
    if startUrl !='' and fileName !='':
        crawler = runoobToPDF(fileName, startUrl)
        crawler.main()

# -*- coding: UTF-8 -*-
import os
import re
import time
import random
import pdfkit
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse  
from time import sleep
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
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
                "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
                "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
                "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
                "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
                "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
                "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
                "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
            ]  
    def crawl(self, url,proxy=None,retriesNum=5):
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
                    print(u"获取网页失败，1s后将获取,倒数第",retriesNum,u"次")
                    return self.crawl(url,retriesNum-1)  
                else:
                    print(u"开始使用代理")
                    time.sleep(1)
                    IP="".join(str(random.choice(self.ipList)).strip())
                    proxy={"http":IP}
                    return self.crawl(url,proxy)
        else:
            try:
                IP="".join(str(random.choice(self.ipList)).strip())   
                proxy={"http":IP} 
                print(url) 
                response=requests.get(url,headers=header,proxies=proxy)
                return response
            except:
                if retriesNum>0:
                    time.sleep(1)
                    IP="".join(str(random.choice(self.ipList)).strip())
                    print(u"正在更换代理，1s后将重新获取,第",retriesNum,u"次")
                    print(u"当前代理是：",proxy)
                    return self.crawl(url,proxy,retriesNum-1)
                else:
                    print(u"代理发生错误，取消代理")
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
        try:
            soup = BeautifulSoup(response.content, 'lxml')
            body = soup.find_all(class_="article-body")
            html = str(body)
            html = htmlTemplate.format(content=html).encode("utf-8")
            return html
        except:
            print("解析失败")
            return            
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
        print(u"总共耗时：%f 秒" % totalTime)
if __name__ == '__main__':
    print("起始地址：")
    startUrl = input()
    print("保存文件名(不需要后缀名)：")
    fileName = input()
    if startUrl !='' and fileName !='':
        crawler = runoobToPDF(fileName, startUrl)
        crawler.main()
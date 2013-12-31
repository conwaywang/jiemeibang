#-*-encoding: utf8 -*-

'''
Created on 2013-12-27
http://news.qq.com/newssh/qiwen.shtml  抽取惊奇新闻
@author: conway
'''
import time
from base import BaseParser
from pyquery import PyQuery as pq

#-*-encoding: utf8 -*-

class QiWen(BaseParser):
    def __init__(self, urlSet=None):
        BaseParser.__init__(self)
        
        self.baseUrl = "http://news.qq.com"
        self.oriUrl = "http://news.qq.com/newssh/qiwen.shtml"
        self.__postedSet = urlSet
        
        self.__urlList = [] #待爬取链接
        self.__index = 0    #当前待爬取url的index
        
    def __del__(self):
        pass
    
    def getQiwen(self):
        if not self.__urlList:
            self.__urlList = self.parseMain()
            self.__index = 0
            
        while self.__index < len(self.__urlList):
            url = self.__urlList[self.__index]
            self.__index += 1
            if not self.__postedSet or url not in self.__postedSet:
                infos = self.__parseNews(url)
                return infos
        return None

    #分析主页面  提取新闻链接
    def parseMain(self, timeInfo=None):
        urlList = []
        urlAll = []

        content = self.getContent(self.oriUrl, "gbk")
        d = pq(content)
        t = d("td").filter(".f14").eq(1).items('a')
        
        #得到当前时间
        if not timeInfo:
            timeInfo = time.strftime('%Y%m%d',time.localtime(time.time()))
        
        for a in t:
            url = a.attr("href")
            url = self.baseUrl+url
            urlAll.append(url)
            if timeInfo in url:
                urlList.append(url)
            #print a.attr("href"), "\n"
            
        if not urlList: #没找到当天的，则返回全部的
            urlList = urlAll
        return urlList
    
    #分析新闻页面 提取内容
    def  __parseNews(self, url):
        infos = {}
        infos['url'] = url
        content = self.getContent(url, "gbk")
        d = pq(content)
        
        #title
        title = d("h1").text()
        infos["title"] = title
        
        #img
        imgs = d("#Cnt-Main-Article-QQ").items("img")
        for img in imgs:
            imgSrc = img.attr("src")
            img.prepend("[img]%s[/img]" % imgSrc)
        
        #content
        paras = d("#Cnt-Main-Article-QQ").items("p")
        for p in paras:
            p("strong").prepend("[b]").append("[/b]")
            p.prepend("[p=30, 2, left]").append("[/p]")
        
        infos["text"] = d("#Cnt-Main-Article-QQ").text()
        return infos
        
    
        
        
    
                
if __name__ == "__main__":
    QiWen().getQiwen()
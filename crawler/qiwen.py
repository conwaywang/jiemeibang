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
            
    def initUrlPool(self, artType, start=None):
        self._urlList = self.__getUrlPool()
        self._index = 0
        self._artType = artType
    
    def getArticle(self):
        while self._index < len(self._urlList):
            url = self._urlList[self._index]
            self._index += 1
            if not self.__postedSet or url not in self.__postedSet:
                infos = self.__getArticleInfo(url)
                return infos
        return None

    #分析主页面  提取新闻链接
    def __getUrlPool(self, timeInfo=None):
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
            
        if not urlList or len(urlList)<3 : #没找到当天的，则返回全部的
            urlList = urlAll
        return urlList
    
    #分析新闻页面 提取内容
    def  __getArticleInfo(self, url):
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
    q = QiWen()
    q.initUrlPool("qiwen")
    q.getArticle()
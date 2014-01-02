#-*- encoding:utf8 -*-
'''
Created on 2013-12-29
笑话 http://www.jokeji.cn/hot.asp
@author: conway
'''
import re
from pyquery import PyQuery as pq
from crawler.base import BaseParser
import urllib

class Joke(BaseParser):
    def __init__(self, postUrls = None):
        BaseParser.__init__(self)
        
        #信息页面
        self.__baseInfoUrl = "http://www.jokeji.cn"
        self.__baseListUrl = "http://www.jokeji.cn/hot.asp?MaxPerPage=22&listtype=title&me_page="
        self.__pageSize = 22
        
        self.__postedUrlSet = postUrls
    
    #
    def initUrlPool(self, artType, start=None):
        self._urlPool = self.__getUrlPool(start)
        self._index = 0
        self._artType = artType
        
    def getArticle(self):
        while self._index < len(self._urlPool):
            url = self._urlPool[self._index]
            self._index += 1
            if not self.__postedUrlSet or url not in self.__postedUrlSet:  
                infos = self.__getArticleInfo(url)
                return infos
        return None
            
    def __getUrlPool(self, start):
        urlList = []
        pageIndex = int(start/self.__pageSize)
        urlIndex = start % self.__pageSize
        
        oriUrl = "%s%d" % (self.__baseListUrl, pageIndex)
        html = self.getContent(oriUrl, "gbk")
        #print html
        p = re.compile(r'<td width="408" align="left"><a href="([^"]*)"')
        for m in p.finditer(html, re.I):
            url = m.group(1)
            #print url
            url = urllib.quote(url.encode("gbk"))
            #print url
            if "http" not in url:
                url = self.__baseInfoUrl + url
            urlList.append(url) 
        
        return urlList[urlIndex:]
        
    #获取页面信息
    def __getArticleInfo(self, url):
        infos = {}
        infos["url"] = url
         
        html = self.getContent(url, "gbk")
        d = pq(html)
        title = d("title").text()
        index = title.find("_")
        if -1 != index:
            title = title[:index]
        text = d("span").filter("#text110").html()
        text = self.getText(text)
        infos['title'] = title
        infos['text'] = text
         
        return infos  
        
if __name__ == "__main__":
    joke = Joke()
    joke.initUrlPool(11)
    joke.getArticle()        
        
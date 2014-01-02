# -*- coding: utf-8 -*-
'''
Created on 2013-12-28
爬取爱美网的部分信息。http://www.lady8844.com
@author: conway
'''
from base import BaseParser
from pyquery import PyQuery as pq
import random

class Aimei(BaseParser):
    beautyUrl = {#"化妆技巧":"http://www.lady8844.com/caizhuang/jnhz/",
                          "护肤方法":"http://www.lady8844.com/hufu/mbhl/",
                          "明星妆容":"http://www.lady8844.com/caizhuang/star/",
                          "健康养生":"http://health.lady8844.com/baojian/"
                          }
    emotionUrl = {
                  "夫妻相处":"http://emotion.lady8844.com/fuqi/",
                  "婆媳关系":"http://emotion.lady8844.com/poxi/",
                  "星座情感":"http://emotion.lady8844.com/xingzuo/",
                  "恋爱技巧":"http://emotion.lady8844.com/lajq/",
                  "男人本色":"http://emotion.lady8844.com/nrbs/",
                  "两性知识":"http://emotion.lady8844.com/sjm/"
                  }
    workUrl = {
               "职场":"http://emotion.lady8844.com/zhichang/"
               }
    babyUrl = {
               "备孕":"http://baby.lady8844.com/yunqian/",
               "分娩":"http://baby.lady8844.com/fenmian/",
               "月子":"http://baby.lady8844.com/chanhou/",
               "新生儿":"http://baby.lady8844.com/xse/"
               }
    urlMap = {"beauty":beautyUrl, "emotion":emotionUrl, "work":workUrl, "baby": babyUrl}
    
    def __init__(self, postedUrlSet=None):
        BaseParser.__init__(self)
        #已获取并发表的集合
        self.__postedUrlSet = postedUrlSet        
        
    #设置新的类型
    def initUrlPool(self, artType, start=None):
        #判断是否从当前类别取文章
        if artType != None and self._artType != artType: #新的类型
            self._artType = artType
            self._urlList = self.__getUrlPool(Aimei.urlMap[self._artType])
            self._index = 0
    
    #随机取一篇文章 infos有title,text, url    
    def getArticle(self):
        while self._index < len(self._urlList):
            url = self._urlList[self._index]
            self._index += 1
            if not self.__postedUrlSet or url not in self.__postedUrlSet:   #找到没有发表过的
                infos = self.__getArticleInfo(url)
                return infos
        return None
    
    #获取各个板块第一页的url列表,并杂糅到一起
    def __getUrlPool(self, maps):
        urlList = []
        for k,v in maps.iteritems():
            urlList.extend(self.__getUrls(v))
        #在这里把所有板块的url乱序   好让各个版面的文章不扎堆
        random.shuffle(urlList)
        return urlList
    
    #获取链接
    def __getUrls(self, url):   
        urlList = [] 
        content = self.getContent(url)
        d = pq(content)
        aList = d("div").filter(".ArtList").items("a")
        for a in aList: 
            url = a.attr("href")
            urlList.append(url)
        return urlList
    
    #获取正文信息项
    def __getArticleInfo(self, url):
        infos = {}
        infos["url"] = url
        
        html = self.getContent(url)
        d = pq(html)
        title = d("h1").text()
        infos["title"] = title
        #print html
        
        #content   
        infos['text'] = self.__getTextFromHtmlContent(html)
        #这里要处理分页的情况
        pages = d("div").filter("#content_pagelist").find("a")
        if pages:   #分页
            pageUrl = self.__getBasePageUrl(url)
            maxPage = d(pages[-2]).text().strip()
            maxPageNum = int(maxPage)
            print "page ",
            for i in range(1, maxPageNum):
                print i,
                page = self.getContent("%s%d.html" %(pageUrl,i))
                infos['text'] += self.__getTextFromHtmlContent(page)
            print 
        return infos
    
    #从页面中抽取正文   并且把图片替换成需要的格式
    def __getTextFromHtmlContent(self, html):
        d = pq(html)
        imgs = d(".endtext").items("img")
        for img in imgs:
            imgSrc = img.attr("src")
            img.prepend("[img]%s[/img]" % imgSrc)
        
        #content
        paras = d(".endtext").items("p")
        for p in paras:
            p.prepend("[p=30, 2, left]").append("[/p]")
        
        text = d(".endtext").text().replace("(点击图片进入下一页)", "")
        return  text
    
    #对url的分页格式进行分析http://www.lady8844.com/caizhuang/jnhz/2013-12-23/1387773111d1395818.html
    def __getBasePageUrl(self, url):
        arr = url.split("/")
        baseUrl = ("/").join(arr[:-1])
        last = arr[-1]
        dotIndex = last.find(".")
        id = last[:dotIndex]
        docType = last[dotIndex:]
        
        return baseUrl+"/"+id+"_"
    
if __name__ == "__main__":
    infos = Aimei().getArticle()
    print infos['title'], '\n', infos['text']
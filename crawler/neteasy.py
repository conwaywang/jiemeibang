#-*-encoding: utf8 -*-
import sys
import re
import json

from base import BaseParser
from pyquery import PyQuery as pq
'''
    author: conway
    date:20131221
            目的：抽取网易新闻排序相关类别的新闻
            网站:  http://news.163.com/rank/
    '''
class NetEasyRank(BaseParser):
    
    def __init__(self, postedUrlSet=None):
        BaseParser.__init__(self)
        
        self.baseurl = "http://news.163.com/rank/"     
        #
        self.__postedUrlSet = postedUrlSet
        #要抽取的类别在页面中 div(.tabBox)的序号。根据这个抽取指定的信息块的url
        self.__typeIndexMap = {
              "ent":5,
              "news":1
              }
    
    #初始化url pool
    def initUrlPool(self, artType, start=None):
        self._urlPool = self.__getUrlPool(self.__typeIndexMap[artType])
        self._index = 0
        self._artType = artType
                          
    #获取指定页面
    def getArticle(self):
        while self._index < len(self._urlPool):
            url = self._urlPool[self._index]
            self._index += 1
            if not self.__postedUrlSet or url not in self.__postedUrlSet:
                infos = self.__getArticleInfo(url)
                return infos
        return None
        
    #divIdx  要抽取的板块在页面中的div的序号
    def __getUrlPool(self, divIdx):
        urlList = []
        content = self.getContent(self.baseurl, "gbk");
        d = pq(content)
        aList = d("div").filter(".tabBox").eq(divIdx).items("a")
        for a in aList:
            url = a.attr("href")
            urlList.append(url)
        return urlList
        
    #正文包含3中类型：photoview形式；单图形式；图片galaery形式
    def __getArticleInfo(self, url):
        infos = {}
        infos["url"] = url
        
        html = self.getContent(url, "gbk")
        d = pq(html)
        #title
        title = d("h1").text()
        infos["title"] = title
        
        #photoview形式 
        if "photoview" in url:
            infos['text'] = self.__getPVText(html)
            return infos
        
        #gallery 图片提取。可能没有
        imgText = ""
        imgs = d("textarea").filter(".hidden").items("img")
        for img in imgs:
            imgSrc = img.attr("src")
            if "s_" in imgSrc: #换成原图
                imgSrc = imgSrc.replace("s_", "")
            imgText += "[p=30, 2, left][img]%s[/img][/p]" % imgSrc
        
        #最后一个div[#endText]一般为正文，且包含图片    
        endText = d("div").filter("#endText")
        t = endText[-1]
        nd = pq(t)
        imgs = nd.items("img")
        for img in imgs:
            imgSrc = img.attr("src")
            if r"cnews/css13/img/end_ent.png" in imgSrc:
                continue
            img.prepend("[img]%s[/img]" % imgSrc)
        paras = nd.items("p")
        for p in paras:
            p.prepend("[p=30, 2, left]").append("[/p]")
        text = nd.text()
    
        infos['text'] = text + imgText
        return infos 
            
            
    #photoview 形式 得到
    def __getPVText(self, html):
        lLabel = '<textarea name="gallery-data" style="display:none;">'
        rLabel = '</textarea>'
        
        index1 = html.find(lLabel)
        if -1 == index1:
            print "pv index1 error"
            return None
        index2 = html.find(rLabel, index1)
        if -1 == index2:
            print "pv index2 error"
            return None
        
        jsonText = html[index1+len(lLabel):index2].strip("  \n\r")
        photoInfo = json.loads(jsonText)
        text = "[p=30, 2, left]%s[/p]" % photoInfo["info"]["prevue"]
        for photo in photoInfo["list"]:
            text += "[img]%s[/img]" % photo["img"]
        return text
            
        
if __name__ == "__main__":
    net = NetEasyRank()
    #url = "http://ent.163.com/photoview/00AJ0003/518625.html#p=9HBCAA8V00AJ0003"
    url = "http://ent.163.com/13/1229/23/9HA3T81B00031H2L.html"
    #url = "http://ent.163.com/13/1230/09/9HB62OLT00032DGD.html"
    net.initUrlPool("ent")
    for i in range(0,3):
        infos =  net.getArticle()
        print "%s\n%s\n%s" %(infos['url'], infos['title'], infos['text'])
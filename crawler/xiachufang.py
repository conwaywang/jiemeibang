#-*-encoding: utf8 -*-
import sys
import re
import os
import time

from base import BaseParser

class XiaChuFang(BaseParser):
    '''
    author: conway
    date:20131218
    目的：抽取下厨房
    网站: http://www.xiachufang.com/recipe/1/" 
    '''
    def __init__(self):
        BaseParser.__init__(self)
        self.name = "xiachufang"
        self.baseurl = "http://www.xiachufang.com/recipe/"        

        #抽取内容存储文件名
        #extract_file_name = self.extract_dir + "/" + self.name
        #self.out_extract_file = open(extract_file_name, "a")
        
        #html标记
        self.htmltagreobj = re.compile("<[^>]+>")
            
    
    #
    def __del__(self):
        #关闭抽取输出文件
        #self.out_extract_file.close()
        pass
               
    #下载一级页面
    def doWork(self):   
        #循环下载，生成一级页面URL
        totalpagenum = 9
        print totalpagenum
        for i in range(0, totalpagenum+1):                   
            url = "%s%d" %(self.baseurl, i)     
            content = self.getContent(url)
            items = self.getInfoItemFromContent(content)
            print items['title'],'/n', items['text']
            
            #super(DoNews, self).writeInfoItem2File(info_item, self.out_extract_file) 
        #
    def getInfoItemFromContent(self, content):
        info_item = {}
        
        #1                  
        articlecontent = self.getArticleContent(content)
        #title
        title = self.getTitle(articlecontent)    
        #图片
        imgSrc = self.getFirstImageSrc(articlecontent)    
        #正文
        text = self.getFormatText(content)
       

        info_item["text"] = "[img]%s[/img]%s" %(imgSrc, text)
        info_item["title"] = title
        info_item["img"] = imgSrc
        return info_item 
        
    #得到post的html范围
    def getArticleContent(self, content):
        startarticle = content.find('<div itemtype="http://schema.org/Recipe" itemscope="">')
        if -1 == startarticle:
            return ""
        end = content.find('<div class="print">', startarticle)
        if -1 == end:
            print "not find text end !"
            sys.exit(1)
            
        articlecontent = content[startarticle:end]
        print articlecontent
        return articlecontent
        
    #得到标题
    def getTitle(self, content):
        title = ""
        starttitle = content.find('<h1 class="page-title" itemprop="name">')
        if -1 != starttitle:
            endtitle = content.find('</h1>', starttitle)
            title = content[starttitle+39:endtitle]
        
        return title
    
    #得到发表时间
    def getFirstImageSrc(self, content):
        src = ""
        #posttime = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        startImg = content.find('<img')
        if -1 != startImg:
            endImg = content.find('>', startImg)
            img = content[startImg:endImg]
            startSrc = img.find('src="')
            if -1 != startSrc:
                endSrc = img.find('"', startSrc+5)
                src = img[startSrc+5:endSrc].strip()
        else:
            print "not find img"
        return src
                     
    #获取替换格式后的正文
    def getFormatText(self, content):
        start = content.find('<h2>')
        end = content.find('<div class="print">', start)
        
        if -1 == start or -1 == end:
            return ""
        #正文区间
        content = content[start:end]
        
        re.sub("<h2>", "[size=5]", content)
        re.sub("</h2>", "[/size]", content)
        
        #table 处理
        re.sub("<table[^>]+>", "[table=50%]", content)
        re.sub("</table>", "[/table]", content)
        re.sub("<tr>", "[tr]", content)
        re.sub("</tr>", "[/tr]", content)
        re.sub("<td[^>]+>", "[/td]", content)
        re.sub("</td[^>]+>", "[/td]", content)
        
        #list
        re.sub("<ol[^>]+>", "[list=1]", content)
        re.sub("</ol>", "[/list]", content)
        re.sub("<li[^>]+>", "[*]", content)
        
        #获取正文
        text = super(XiaChuFang, self).getText(content)
        return text
                
aa = XiaChuFang()
aa.doWork()

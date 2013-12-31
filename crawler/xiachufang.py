#-*-encoding: utf8 -*-
import sys
import re


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
        
    #
    def __del__(self):
        pass
               
    #获取指定页面
    def getPageInfo(self, start):   
        url = "%s%d" %(self.baseurl, start)     
        content = self.getContent(url)
        #print content
        items = self.getInfoItemFromContent(content)
        items['url'] = url
        #print items['text']
        return items
        
        #
    def getInfoItemFromContent(self, content):
        info_item = {}
        
        #1                  
        articlecontent = self.getArticleContent(content)
        if not articlecontent:
            return None
        #print 'articlecontent:', articlecontent, "\n\n"
        #title
        title = self.getTitle(articlecontent)   
        if not title:
            return None 
        #图片
        imgSrc = self.getFirstImageSrc(articlecontent)    
        if not imgSrc:
            return None
        #正文
        text = self.getFormatText(articlecontent)
        if not text:
            return None
        #print "title:%s\nsrc:%s\ntext:%s\n" %(title, imgSrc, text)
       
        info_item["text"] = "[img]%s[/img]\n\n%s" %(imgSrc, text)
        info_item["title"] = title
        info_item["img"] = imgSrc
        return info_item 
        
    #得到post的html范围
    def getArticleContent(self, content):
        startarticle = content.find('<div itemscope itemtype="http://schema.org/Recipe">')
        if -1 == startarticle:
            print "startarticle error"
            return None
        end = content.find('<div class="print">', startarticle)
        if -1 == end:
            print "not find text end !"
            sys.exit(1)
            
        articlecontent = content[startarticle:end]
        return articlecontent
        
    #得到标题
    def getTitle(self, content):
        title = ""
        starttitle = content.find('<h1 class="page-title" itemprop="name">')
        if -1 != starttitle:
            endtitle = content.find('</h1>', starttitle)
            title = content[starttitle+39:endtitle]
            return title
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
        
        if -1 == start:
            return ""
        #正文区间
        content = content[start:]
        content = super(XiaChuFang, self).unEscape(content)
        #print "content:%s" % content
        
        content = re.sub("<h2>", "[size=5]", content)
        content = re.sub("</h2>", "[/size]", content)
        
        #table 处理
        content = re.sub("<table[^>]+>", "[table=50%]", content)
        content = re.sub("</table>", "[/table]", content)
        content = re.sub("<tr>", "[tr]", content)
        content = re.sub("</tr>", "[/tr]", content)
        content = re.sub("<td[^>]+>", "[td]", content)
        content = re.sub("</td>", "[/td]", content)
        
        #list
        content = re.sub("<ol[^>]+>", "[list=1]", content)
        content = re.sub("</ol>", "[/list]", content)
        content = re.sub("<li[^>]+>[\n\r]*", "[*]", content)
        
        content = re.sub("[  ]", "", content)
        content = re.sub("\n+", "\n", content)
        #去掉所有html标记
        text = re.sub("<[^>]+>", "", content)
        return text

#aa = XiaChuFang()
#aa.getPageInfo(1)
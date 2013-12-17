#-*-encoding: utf8 -*-
import sys
import re
import os
import time

from download import Download
from mysqlconnector import MysqlConnector
from base import BaseParser

class DoNews(BaseParser):
    '''
    author: conway
    date:20120610
    目的：抽取“互联网的那点事”产品介绍页面信息
    网站: http://x.donews.com/news/
    抽取方法：
        1、一级页面，即分页页面直接生成。从1到总页数范围
        2、二级页面，即最终产品介绍页面。利用正则表达式抽取文本信息
    说明：
    网址类型分别为：
        1、http://x.donews.com/news/

    '''
    def __init__(self):
        BaseParser.__init__(self)
        self.name = "donews"
        self.domain = "http://x.donews.com/news/"        
        #当前是第几次更新。用于一级页面存储时的文件前缀
        #self.fileprefix = "2_"
        #抽取内容存储文件名
        self.extract_file_name = self.extract_dir + "/" + self.name
        self.out_extract_file = open(self.extract_file_name, "w")
        
        #一级页面类别
        self.starturldict = {'chuangye':'http://x.donews.com/news/index.php?pp='}
        
        #二级页面url正则表达式
        self.infourlreobj = re.compile('<a href="(http://x\.donews\.com/news/\d+/\d+\.shtml)"', re.DOTALL)
        #二级页面url集合
        self.infourlset = set()
        
        #html标记
        self.htmltagreobj = re.compile("<[^>]+>")
        
        #页面目录
        print os.path.exists(self.name)
        if not os.path.exists(self.name):
            os.mkdir(self.name)
            
        #分类别一级页面目录
        for cat in self.starturldict.keys():
            catdir = self.name+"/"+cat
            if not os.path.exists(catdir):
                os.mkdir(catdir)
        
        #二级页面，最终信息页面目录
        self.urldir = self.name+"/"+"info"
        if not os.path.exists(self.urldir):
            os.mkdir(self.urldir)
    
    #
    def __del__(self):
        #关闭抽取输出文件
        self.out_extract_file.close()
    
    
    #从首页分析总的页数
    def getTotalPageNum(self, content):   
        #print content
        startindex = content.find('<span>共['.decode("utf8"))
        if -1 != startindex:
            endindex = content.find("]页".decode("utf8"), startindex)
            return  int(content[startindex+8:endindex])
    
    #统计目录下下载的一级页面数
    def statDownloadPageNum(self):
        return len(os.walk(self.name)[2])
    
    #分别下载3类一级页面
    def work(self):
        for cat,starturl in self.starturldict.iteritems():
            dir = self.name+"/"+cat
            self.doWork(starturl, dir)
            
    
    #下载一级页面
    def doWork(self, baseurl, dir):   
        #循环下载，生成一级页面URL
        firstpagefilename = "%s/%s0" % (dir, self.fileprefix)
        firstpageurl = baseurl+"0"
        totalpagenum = 9
        print totalpagenum
        for i in range(0, totalpagenum+1):                   
            url = "%s%d" %(baseurl,i*50)
            filename = "%s/%s%d" % (dir, self.fileprefix, i*50)        
            content = self.getContent(url, filename)
            
            #分析该页面含的二级页面是否已经全部下载, 如果全部下载，则不用继续下载一级页面了
            level2Urls = self.getUnParsedUrl(content)
            if len(level2Urls) == 0:
                print "no unparsed url!"
                break
    
    #得到url或filename对应的文件内容
    def getContent(self, url , filename, charset="utf8"):
        #判断该分页页面是否存在
        if os.path.isfile(filename):
            filehandler = open(filename, "r")
            content = filehandler.read()
            filehandler.close()
        else:
            content = self.download.get(url)
            #写入文件
            filehandler = open(filename, "w")
            filehandler.write(content)
            filehandler.close()
        content = content.decode(charset)
        return content
        
    #给定url
    #1、判断url是否已下载 mysql 
    #2、未下载  下载url
    #3、提取页面内容 并存储到数据库中
    def parsePage(self,url):
        if not url:
            return
        if self.mysqlconnector.isURLDownload(url):
           return

        #确定页面是否已经下载
        filename = self.urldir+"/"+url.split("/")[-1]
        print filename     
        #解析网页内容  1、正文 2、标题 3、时间
        content = self.getContent(url, filename)
        #得到信息项
        info_item = self.getInfoItemFromContent(content)
            
        #print "[%s][%s][%s]" % (info_item['text'],info_item['title'], info_item['posttime'])
        
        #添加信息到数据库，并将该url标记为下载状态
        info_item['url'] = url
        super(DoNews, self). insert2Table(info_item, self.out_extract_file, self.domain) 
        
    #得到post的html范围
    def getArticleContent(self, content):
        startarticle = content.find('<div class="content_body">')
        if -1 == startarticle:
            return ""
        end = content.find('<div class="jiathis_donews">', startarticle)
        if -1 == end:
            print "not find text end !url[%s]" % url
            sys.exit(1)
            
        articlecontent = content[startarticle:end]
        return articlecontent
        
    #得到标题
    def getTitle(self, content):
        title = ""
        starttitle = content.find('<h1 class="title">')
        if -1 != starttitle:
            endtitle = content.find('</h1>', starttitle)
            title = content[starttitle+18:endtitle]
        
        return title
    
    #得到发表时间
    def getTime(self, content):
        posttime = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        starttime = content.find('</a>|')
        if -1 != starttime:
            endtime = content.find('|', starttime+5)
            #starttime = content.find('<span>', starttime);
            posttime = content[starttime+5:endtime].strip().split(" ")[0]
            #这里格式如：2012-03-02 20:50
        else:
            print "not find time"
        return posttime
    
    #现在没有标签，从标题里抽下可能的名字
    def getTag(self, title):
        tag_list = []
        start_index = title.find(":")
        en_flag = 1
        if -1 == start_index:
            start_index = title.find("：")
        if -1 == start_index:
            start_index = title.find("—")
        if -1 == start_index:
            start_index = title.find("-")
        if -1 != start_index:
            prob_name = title[0:start_index]
            #print "***"+prob_name
            for i in range(0,start_index):
                if ord(prob_name[i]) > 127:
                    en_flag = 0
            if en_flag:        
                tag_list.append(prob_name)
                return tag_list
            #print "ok"
        i = 0
        end = len(title)
        while i < end:
            ch = title[i:i+1]
            #print ch
            if ch.isalpha():
                str_len = 0
                start_index = i
                #print ord(ch)
                while i<end and ord(ch[0])<127 and (ch.isalpha() or ch.isdigit() or ch==" " or ch=="."):
                    #print ch," ",ord(ch)
                    str_len += 1
                    i += 1
                    ch = title[i:i+1]
                if str_len > 3 and title[start_index:i] not in tag_list:
                    #print title," * ",title[start_index:i]
                    tag_list.append(title[start_index:i])
            i = i+1
            
        return tag_list  
    
    #从分页展示页面中提取最终页面的url
    def getInfoUrlFromPage(self, content):
        urllist = []
        #提取信息页面url
        startindex = content.find('[<a href="http://x.donews.com/news">创业新闻</a>]'.decode("utf8"))
        while startindex != -1:
            linkstart = content.find("href=\"", startindex + 55)
            linkend = content.find('"', linkstart+6)
            if linkstart != -1 and linkend != -1:
                urllist.append(content[linkstart+6:linkend])
            startindex = content.find('[<a href="http://x.donews.com/news">创业新闻</a>]'.decode("utf8"), linkend)
            
        return urllist
    
    #分析一级页面，提取二级页面URL。并过滤已经提取的URL
    def getUnParsedUrl(self, content):
        unparsedurls = []
        urllist = self.getInfoUrlFromPage(content)
        for url in urllist:
            if 0 == self.mysqlconnector.isURLDownload(url):
                unparsedurls.append(url)
        
        return unparsedurls
        
    #分析一级页面，提取其中符合条件的二级页面url，得到对应二级页面html文档，提取正文信息
    def doParse(self):
        #分析各个类别
        for cat in self.starturldict.keys():
            #文件目录
            dirname = self.name + "/" + cat
            
            for filename in os.listdir(dirname):
                if not filename.startswith(self.fileprefix):
                    continue
                    
                filename =  dirname+"/"+filename 
                print filename
                if os.path.isfile(filename):
                    #读取文件
                    #读取文件
                    content = BaseParser.getFileContent(self, filename)
                    #分析文件
                    infourllist = self.getInfoUrlFromPage(content)
                    #print infourllist

                    #循环分析每篇内容
                    for url in infourllist:
                        print url
                        if url.find("/14818.html") != -1:
                            continue
                        self.parsePage(url)
    #
    def getInfoItemFromContent(self, content):
        info_item = {}
        
        #1                  
        articlecontent = self.getArticleContent(content)
        #正文
        text = super(DoNews, self).getText(articlecontent)
        text_with_link = super(DoNews, self).getTextWithLink(articlecontent)
        #2 title
        title = self.getTitle(content)        
        #3 time
        posttime = self.getTime(content)
        #4 tag
        tag_list = self.getTag(title)
                                
        #图片
        img_list = super(DoNews, self).getImgSrcList(articlecontent)
        #可能的名字
        name_list = super(DoNews, self).getNameList(articlecontent)
        
        info_item["text"] = text
        info_item["text_with_link"] = text_with_link
        info_item["title"] = title
        info_item["posttime"] = posttime
        info_item["img_list"] = img_list
        info_item["name_list"] = name_list
        info_item["tag_list"] = tag_list
        
        return info_item 
        
    #提取正文内容。[url],[title],[names],[content],[images],[createtime]
    def doExtract(self):
        url_list = self.mysqlconnector.getUrls(self.domain)
        for row in url_list:
            url = row[0]
            print url
            names = url.split("/")
            filename = names[-1]
            if not filename:
                print "error"
                return

            filename = self.urldir + "/" + filename
            print filename
            if os.path.isfile(filename):
                #读取文件
                content = BaseParser.getFileContent(self, filename)    
                #得到信息项
                info_item = self.getInfoItemFromContent(content)
                info_item['url'] = url
                super(DoNews, self).writeInfoItem2File(info_item, self.out_extract_file)      
    
#设置编码
reload(sys)
sys.setdefaultencoding("utf8")
                
aa = DoNews()
#下载含有文章链接的分页页面
aa.work()
#分析提取分页页面中信息
aa.doParse()

#aa.doExtract()

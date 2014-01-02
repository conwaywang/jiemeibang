#-*-encoding: utf8 -*-
import re
import os
import time,datetime

from abc import ABCMeta,abstractmethod
from util.download import Download

class BaseParser(object):
    '''
        edit:20120524    时间戳作为文件名前缀
    '''
    def __init__(self):     
        #页面下载器
        self.__download = Download()
        
        self._artType = ""  #板块
        self._urlList = []  #待爬取链接
        self._index = 0     #当前待爬取url的index
    
    #用时间戳设置前缀
    def setFilePrefix(self):
        nowtime = datetime.datetime.now()
        self.fileprefix = nowtime.strftime('%Y%m%d')+"_"
    
    #得到url或filename对应的文件内容。如果没有下载则下载并存储
    def getContent(self, url ,  charset="utf8"):
        content = self.__download.get(url, charset)
        #print content, "\n\n\n"
        #写入文件
        #filehandler = open(filename, "w")
        #filehandler.write(content.encode(charset))
        #filehandler.close()
            
        #content = content.decode(charset, "ignore")
        return content
    
    #得到文件内容并返回
    def getFileContent(self, filename, charset="utf8"):
        file_object = open(filename, "r")
        file_content = file_object.read()
        file_object.close()    
        content = file_content.decode(charset, "ignore")
        
        return content
        
    def getImgSrcList(self, articlecontent):
        img_list = []
        img_src_end = 0
        articlecontent = articlecontent.lower()
        imgstart = articlecontent.find("<img")
        while -1 != imgstart:
            img_src_start = articlecontent.find("src=\"", imgstart)
            if -1 != img_src_start:
                img_src_start = img_src_start + 5
                img_src_end = articlecontent.find("\"", img_src_start)
            else:
                img_src_start = articlecontent.find("src='", imgstart)
                if -1 != img_src_start:
                    img_src_start =  img_src_start + 5
                    img_src_end = articlecontent.find("'", img_src_start)
                else:
                    break
            if -1 == img_src_end:
                break
                
            img_list.append(articlecontent[img_src_start:img_src_end])
            #print imgstart,img_src_start,img_src_end
            imgstart = articlecontent.find("<img", img_src_end)
            
        return img_list

    #得到正文内容
    def getText(self, articlecontent):
        if not articlecontent:
            return ""
        startptag = articlecontent.find("<p")
        text = ""
        if -1 == startptag:
            #print "here"
            text = re.sub("<br ?/?>", "\n", articlecontent)
            #print text
            text = re.sub("<[^>]+>", "", text) + "\n"
            #print "********"+text+"********"
        while startptag != -1:
            endptag = articlecontent.find("</p>", startptag+3)
            if endptag == -1:
                endptag = articlecontent.find("<p", startptag+3)
                if -1 == endptag:
                    text = text + re.sub("<[^>]+>", "", articlecontent[startptag:]) + "\n"
                    break
                else:
                    text = text + re.sub("<[^>]+>", "", articlecontent[startptag:endptag]) + "\n"
                    startptag = endptag + 4
            else :
                #print articlecontent[startptag:endptag]
                text = text + re.sub("<[^>]+>", "", articlecontent[startptag:endptag]) + "\n"
                #print "***"+text+"***"
                startptag = articlecontent.find("<p",endptag+4)
            
        return self.unEscape(text)
    
    #html 转义字符处理
    def unEscape(self, content):
        special_char_dict = {"&#34;":"\"", "&#38;":"&", "&#8211;":"–", "&#8220;":"\"", \
            "&#8212;":"—", "&#8221;":"\"", "&#8216;":"\"", "&#8217;":"\"", "&#8218;":"?", \
            "&#038;":"&", "&#8230;":"…", "&#8243;":"\"", "&#215;":"×", "&nbsp;":" ", "&#12288;":" "}
        
        for str1,str2 in special_char_dict.iteritems():
            content = content.replace(str1, str2)
        
        return content  
    
    #抽取出的信息项写入文件
    def writeInfoItem2File(self, info_item, file_handler):
        file_handler.write("[url]\n%s" % (info_item['url']))
        
    
    @abstractmethod
    def getArticle(self):
        '''获取相应文章信息的接口
                                        从urlPool中获取一个url，判断是否为未下载过的，从总抽取对应的信息
            return map keys:url,title,text
        '''
        pass
    
    @abstractmethod
    def initUrlPool(self, artType, start=None):
        '''给定的信息，生成待获取url列表
        '''
        pass
    

    
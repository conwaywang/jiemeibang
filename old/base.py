#-*-encoding: utf8 -*-
import sys
import re
import os
import time,datetime
import socket

from download import Download
from mysqlconnector import MysqlConnector
from procname import NameEvaluator
from invest_extract import InvestExtractor

class BaseParser(object):
    '''
        edit:20120524    时间戳作为文件名前缀
    '''
    def __init__(self):
        self.name = ""
        self.domain = ""        
        #当前是第几次更新。用于一级页面存储时的文件前缀
        self.fileprefix = "3_"
        
        #页面下载器
        self.download = Download()
        #数据库操作
        self.mysqlconnector = MysqlConnector()
        #产品名打分评价
        self.nameevaluator = NameEvaluator()
        #投资信息抽取
        self.investextractor = InvestExtractor()

        #extract path
        self.extract_dir = "extract"
        #
        #设置文件前缀
        self.setFilePrefix();
    
    #用时间戳设置前缀
    def setFilePrefix(self):
        nowtime = datetime.datetime.now()
        self.fileprefix = nowtime.strftime('%Y%m%d')+"_"
    
    #得到url或filename对应的文件内容。如果没有下载则下载并存储
    def getContent(self, url , filename, charset="utf8"):
        #判断该分页页面是否存在
        if os.path.isfile(filename):
            filehandler = open(filename, "r")
            content = filehandler.read()
            filehandler.close()
        else:
            content = self.download.get(url, charset)
            #写入文件
            filehandler = open(filename, "w")
            filehandler.write(content.encode(charset))
            filehandler.close()
        content = content.decode(charset, "ignore")
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
    
    def getNameList(self, articlecontent):
        name_list = []
        url_start = articlecontent.find("<a ")
        #print "***",url_start
        while url_start != -1:
            name_start = articlecontent.find(">",  url_start) + 1
            name_end = articlecontent.find("<", name_start)
            name = articlecontent[name_start:name_end].strip(" ()")
            if len(name) > 0 and name not in name_list and -1 == name.find("http://"):
                name_list.append(name)
                #print name
            url_start = articlecontent.find("<a ", name_end)
        return name_list
    
    def getTextWithLink(self, articlecontent):
        startptag = articlecontent.find("<p")
        text = ""
        if -1 == startptag:
            articlecontent = re.sub("[\n\r]", "", articlecontent)
            para_con = re.sub("(<br ?/?>)+", "\n", articlecontent)
            text = self.getParaContentWithLink(para_con)
            #print "****"+text
        while startptag != -1:
            endptag = articlecontent.find("</p>", startptag+3)
            if endptag == -1:
                para_con = articlecontent[startptag+3:]
            else:
                para_con = articlecontent[startptag:endptag]
            text += self.getParaContentWithLink(para_con)
             
            if endptag == -1:
                break
            else :
                startptag = articlecontent.find("<p>",endptag+4)
            #print startptag," ",endptag
            
        return self.unEscape(text)            
    
    def getParaContentWithLink(self, para_con):
        text = ""
        htmlendtag = -1
        htmltagstart = para_con.find("<")
        while htmltagstart != -1:
            text += para_con[htmlendtag+1:htmltagstart]
            htmlendtag = para_con.find(">", htmltagstart)
            if para_con[htmltagstart+1:htmltagstart+2]=="a" or \
                (para_con[htmltagstart+2:htmltagstart+3]=="a" and para_con[htmltagstart+1:htmltagstart+2]=="/"):
                text += para_con[htmltagstart:htmlendtag+1]
            htmltagstart = para_con.find("<", htmlendtag)
        text += para_con[htmlendtag+1:]
        text = text + "\n"
        return text
        
    
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
            "&#8212;":"—", "&#8221;":"\"", "&#8216;":"\"", "&#8217;":"\"", "&#8218;":"‚", \
            "&#038;":"&", "&#8230;":"…", "&#8243;":"\"", "&#215;":"×", "&nbsp;":" ", "&#12288;":" "}
        
        for str1,str2 in special_char_dict.iteritems():
            content = content.replace(str1, str2)
        
        return content  
    
    #抽取出的信息项写入文件
    def writeInfoItem2File(self, info_item, file_handler):
        info_item['text_with_link'] = re.sub(" ([ \t]*\n[ \t]*){2,}", "\n", info_item['text_with_link'])
        #print len(info_item['name_list']), len(info_item['tag_list'])
        name_list = info_item['tag_list'] + info_item['name_list']
        #print len(name_list)
        name_score = self.nameevaluator.EvaluateName(name_list, info_item['title'])
        name_info = ""
        max_name = ""
        max_score = 0
        for name in name_score.keys():
            if name_score[name] > max_score:
                max_name = name
                max_score = name_score[name]
                name_info = "%s[%d]" % (max_name, max_score)
        
        invest_sentence_list = self.investextractor.ExtractSentence(info_item['text'])
        file_handler.write("[url]\n%s\n[title]\n%s\n[names]\n%s\n[images]\n%s\n[createtime]\n%s\n[content]\n%s[invest]\n%s\n============\n"
                    % (info_item['url'], info_item['title'], name_info, ",".join(info_item['img_list']),
                    info_item['posttime'], info_item['text_with_link'], "\n".join(invest_sentence_list)))
        #file_handler.write("[url]\n%s\n[title]\n%s\n[names]\n%s\n[images]\n%s\n[createtime]\n%s\n[content]\n%s\n============\n"
        #            % (info_item['url'], info_item['title'], name_info, ",".join(info_item['img_list']),
        #           info_item['posttime'], info_item['text_with_link']))
        
    #    
    def insert2Table(self, info_item, file_handler, domain):
        if self.mysqlconnector.addPost2PostInfo(info_item['title'], info_item['posttime'], info_item['url'], info_item['text'], domain):
            self.mysqlconnector.addURL2Download(info_item['url'])
            self.writeInfoItem2File(info_item, file_handler)
    
        
        
        
#设置编码
reload(sys)
sys.setdefaultencoding("utf8")

#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2013-12-19

@author: conway

自动获取数据并发帖控制程序
'''
import random
import time
import sys

from util.conf import Conf
from crawler.xiachufang import XiaChuFang
from util.discuzRobot import DiscuzRobot
from crawler.aimei import Aimei
from crawler.qiwen import QiWen
from crawler.joke import Joke
from crawler.neteasy import NetEasyRank

class Post():
    fidMap = {"beauty":45, "emotion":41, "work":47, "baby":42, "ent":46, "news":2}
    
    def __init__(self):
        self.crawlerConf = Conf("../conf/crawlerConf")
        self.userConf = Conf("../conf/userConf")
        
        #加载Url
        self.urlFile = open(self.crawlerConf.get("crawler", "url_file_name"), "r+")
        self.__postedSet = set()
        self.initUrlSet()
        
        #自动发帖
        print "-----start get robot list------"
        self.formUrl = self.userConf.get("post", "url")
        self.robotList = self.getDiscuzRobotList()

        #下厨房
        self.xiachufang = XiaChuFang()
        self.start = int(self.crawlerConf.get("xiachufang", "start"))
        self.minPerDay = int(self.crawlerConf.get("xiachufang", "min_post_per_day"))
        self.maxPerDay = int(self.crawlerConf.get("xiachufang", "max_post_per_day"))  
        
        #奇闻
        self.qiwen = QiWen(self.__postedSet)
        self.maxQiwenPerDay = int(self.crawlerConf.get("qiwen", "max_post_per_day"))
        
        #美容养生
        self.aimei = Aimei(self.__postedSet)
        self.maxAimeiPerDay = int(self.crawlerConf.get("aimei", "max_post_per_day"))
        
        #joke
        self.joke = Joke()
        self.maxJokePerDay = int(self.crawlerConf.get("joke", "max_post_per_day"))
        self.jokeStart = int(self.crawlerConf.get("joke", "start"))
        
        #neteasy
        self.neteasy = NetEasyRank()
        self.maxNetPerDay = int(self.crawlerConf.get("neteasy", "max_post_per_day"));
        
        
    def __del__(self):
        self.unInitUrlSet()
            
    #init已爬取url集合
    def initUrlSet(self):
        for line in self.urlFile.readlines():
            self.__postedSet.add(line.strip("\n "))
        print "set_size:", len(self.__postedSet)
    
    #释放url set
    def unInitUrlSet(self):
        if not self.urlFile:
            self.urlFile.close()
    
    #保存已爬取的url到文件
    def saveCrawleredUrl(self, url):
        #print self.urlFile
        if self.urlFile:
            self.urlFile.seek(0, 2)  #移动到文件结尾 
            self.urlFile.write(url+"\n") 
            self.urlFile.flush()   
        else:
            print "urlFile error"
            sys.exit()   
    
    def getDiscuzRobotList(self):
        robotList = []
        
        users = self.userConf.get("post", "user").split(",")
        pwds = self.userConf.get("post", "password").split(",")
        
        if len(users) != len(pwds):
            return None
        
        for (u,p) in zip(users, pwds):
            r = DiscuzRobot(self.formUrl, u, p)
            if r.login():   #成功登陆才加入
                robotList.append(r)
        return robotList
                
        
    def postCtrlXiachufang(self):
        fid = 43    #板块id
        #读取指定范围内的篇数
        num = random.randint(self.minPerDay, self.maxPerDay)
        end = self.start + num
        
        print "\n\n---------start post chufang----------------"
        for i in range(self.start, end):
            print "--%d--" %(i)
            textInfo = self.xiachufang.getPageInfo(i)
            if not textInfo:   #信息获取出错
                continue
            #print "title:%s\ntext:%s\n" %(infos['title'], infos['text'])
            res = self.post(fid , textInfo["title"], textInfo["text"])
            if 0 == res:
                print "publish success!", textInfo['url']
                self.__postedSet.add(textInfo['url'])
                self.saveCrawleredUrl(textInfo['url'])
            else:
                print "publish failed: ", textInfo['url']
        #保存配置    
        self.crawlerConf.set("xiachufang", "start", end)
       
    #发表奇闻异事 
    def postCtrlQiWen(self):
        fid = 39 #板块ID
        
        print "\n\n---------start post qiwen----------------"
        for i in range(0, self.maxQiwenPerDay):
            print "--%d--" %(i)
            textInfo = self.qiwen.getQiwen()
            if not textInfo:
                break #跳出
            res = self.post(fid, textInfo['title'], textInfo['text'])
            if 0 == res: #发表成功
                print "publish success!", textInfo['url']
                self.__postedSet.add(textInfo['url'])
                self.saveCrawleredUrl(textInfo['url'])
            else:
                print "publish failed: ", textInfo['url']
    
    #发表美容养生
    def postAimei(self, artType):
        fid = Post.fidMap[artType] #板块ID
        
        print "\n\n---------%s----------------" %(artType)
        self.aimei.initUrlPool(artType)  #设置新的类型
        for i in range(0, self.maxAimeiPerDay):
            print "--%d--" %(i)
            textInfo = self.aimei.getArticle()
            if not textInfo:    #全部获取
                break
            #print "%s\n%s\n" %( textInfo['title'], textInfo['text'])
            res = self.post(fid, textInfo['title'], textInfo['text'])
            if 0 == res:
                print "publish success!", textInfo['url']
                self.__postedSet.add(textInfo['url'])
                self.saveCrawleredUrl(textInfo['url'])
            else:
                print "publish failed: ", textInfo['url']
        
    #发表笑话
    def postJoke(self):
        fid = 40  
        
        print "\n\n---------jokes----------------" 
        self.joke.initUrlPool(self.jokeStart)
        for i in range(0, self.maxJokePerDay):
            print "--%d--" %(i)
            textInfo = self.joke.getArticle()
            if not textInfo:    #全部获取
                break
            
            self.jokeStart += 1
            #print "%s\n%s\n" %( textInfo['title'], textInfo['text'])
            res = self.post(fid, textInfo['title'], textInfo['text'])
            if 0 == res:
                print "publish success!", textInfo['url']
            else:
                print "publish failed: ", textInfo['url'] 
        #保存start配置
        self.crawlerConf.set("joke", "start", self.jokeStart)
        
    #发表娱乐 新闻
    def postNeteasy(self, artType):
        fid = Post.fidMap[artType]
        
        print "\n\n---------%s----------------" %(artType)
        self.neteasy.initUrlPool(artType)  #设置新的类型
        for i in range(0, self.maxNetPerDay):
            print "--%d--" %(i)
            textInfo = self.neteasy.getArticle()
            if not textInfo:    #全部获取
                break
            #print "%s\n%s\n" %( textInfo['title'], textInfo['text'])
            res = self.post(fid, textInfo['title'], textInfo['text'])
            if 0 == res:
                print "publish success!", textInfo['url']
                self.__postedSet.add(textInfo['url'])
                self.saveCrawleredUrl(textInfo['url'])
            else:
                print "publish failed: ", textInfo['url']
            
    #随机选取已登录用户发表文章
    def post(self, fid, title, text, userIndex=None):
        if not userIndex:
            #随机挑选一个用户
            userIndex = random.randint(0, len(self.robotList)-1)
        print '\tuserIndex:', userIndex
        #发表文章
        res = self.robotList[userIndex].publish(fid, title, text)  
        #暂停时间
        time.sleep(random.randint(15,20))
        
        return res  
        
            
if __name__ == '__main__':
    postCtrl = Post()
    #postCtrl.postCtrlXiachufang()
    #postCtrl.postCtrlQiWen()
    #postCtrl.postAimei("beauty")
    #postCtrl.postAimei("emotion")
    #postCtrl.postAimei("work")
    #postCtrl.postAimei("baby")
    #postCtrl.postJoke()
    postCtrl.postNeteasy("ent")
                
            
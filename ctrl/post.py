#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2013-12-19

@author: conway

自动获取数据并发帖控制程序
'''
import random
import time

from util.conf import Conf
from crawler.xiachufang import XiaChuFang
from util.discuzRobot import DiscuzRobot

class Post():
    def __init__(self):
        self.crawlerConf = Conf("../conf/crawlerConf")
        self.userConf = Conf("../conf/userConf")
        
        #自动发帖
        print "-----start get robot list------"
        self.formUrl = self.userConf.get("post", "url")
        self.robotList = self.getDiscuzRobotList()

        #下厨房
        self.xiachufang = XiaChuFang()
        self.start = int(self.crawlerConf.get("xiachufang", "start"))
        self.minPerDay = int(self.crawlerConf.get("xiachufang", "min_post_per_day"))
        self.maxPerDay = int(self.crawlerConf.get("xiachufang", "max_post_per_day"))  
        
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
        
        for i in range(self.start, end):
            print "***start get ", i
            #获取该文章信息
            infos = self.xiachufang.getPageInfo(i)
            
            if not infos:   #信息获取出错
                continue
            #print "title:%s\ntext:%s\n" %(infos['title'], infos['text'])
            #随机挑选一个用户
            userIndex = random.randint(0, len(self.robotList)-1)
            self.robotList[userIndex].publish(fid , infos["title"], infos["text"])
            time.sleep(2)
        self.crawlerConf.set("xiachufang", "start", i)
            
if __name__ == '__main__':
    postCtrl = Post()
    postCtrl.postCtrlXiachufang()
                
            
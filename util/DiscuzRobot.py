#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2013-12-16

@author: conway
'''

import urllib2, urllib, cookielib, re, time

class DiscuzRobot:

    def __init__(self, forumUrl, userName, password, proxy=None):
        ''' 初始化论坛url、用户名、密码和代理服务器 '''
        self.forumUrl = forumUrl
        self.userName = userName
        self.password = password
        self.formhash = ''
        self.isLogon = False
        self.isSign = False
        self.xq = ''
        self.jar = cookielib.CookieJar()
        if not proxy:
            openner = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar))
        else:
            openner = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.jar), urllib2.ProxyHandler({'http' : proxy}))
        urllib2.install_opener(openner)

    def login(self):
        ''' 登录论坛 '''
        url = self.forumUrl + "/member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&inajax=1";
        postData = urllib.urlencode({'username': self.userName, 'password': self.password, 'answer': '', 'cookietime': '2592000', 'handlekey': 'ls', 'questionid': '0', 'quickforward': 'yes', 'fastloginfield': 'username'})
        req = urllib2.Request(url, postData)
        content = urllib2.urlopen(req).read()
        if self.userName in content:
            self.isLogon = True
            print self.userName, 'login success!'
            #print content
            self.initFormhashXq()
            return True
        else:
            print self.userName, 'login faild!'
            return False

    def initFormhashXq(self):
        ''' 获取formhash和心情 '''
        content = urllib2.urlopen(self.forumUrl + '/plugin.php?id=dsu_paulsign:sign').read().decode('utf8')
        #print content
        rows = re.findall(r'<input type=\"hidden\" name=\"formhash\" value=\"(.*?)\" />', content)
        if len(rows) != 0:
            self.formhash = rows[0]
            print 'formhash is: ' + self.formhash
        else:
            print 'none formhash!'
        

    def reply(self, fid, tid, subject=u'', msg=u'支持~~~顶一下下~~嘻嘻'):
        ''' 回帖 '''
        url = self.forumUrl + '/forum.php?mod=post&action=reply&fid={}&tid={}&extra=&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'.format(fid, tid)
        #print url
        postData = urllib.urlencode({'formhash': self.formhash, 'message': msg, 'subject': subject, 'posttime':int(time.time()) })
        req = urllib2.Request(url, postData)
        content = urllib2.urlopen(req).read().decode('utf8')
        #print content
        if u'发布成功' in content:
            print 'reply success!'
        else:
            print 'reply faild!'

    def publish(self, fid, subject=u'发个帖子测试一下下，嘻嘻~~~', msg=u'发个帖子测试一下下，嘻嘻~~~'):
        ''' 发帖 '''
        url = self.forumUrl + '/forum.php?mod=post&action=newthread&fid={}&extra=&topicsubmit=yes'.format(fid)
        postData = urllib.urlencode({'formhash': self.formhash, 'message': msg, 'subject': subject, 'posttime':int(time.time()), 'addfeed':'1', 'allownoticeauthor':'1', 'checkbox':'0', 'newalbum':'', 'readperm':'', 'rewardfloor':'', 'rushreplyfrom':'', 'rushreplyto':'', 'save':'', 'stopfloor':'', 'typeid':'', 'uploadalbum':'', 'usesig':'1', 'wysiwyg':'0' })
        req = urllib2.Request(url, postData)
        content = urllib2.urlopen(req).read().decode('utf8')
        # print content
        if subject in content:
            print 'publish success!'
        else:
            print 'publish faild!\n'#, content


'''
板块  fid
身边新闻    2
奇闻异事   39
嫣然一笑  40
情感婚姻 41
亲子乐园 42
下得厨房 43
逛街指南  44
美容养生  45
我们都再看 46
职来职往   47
我们自己的生活驿站 49
'''
    

if __name__ == '__main__':
    robot = DiscuzRobot('http://184.82.118.42', u'红尘无痕', 'password4jiemeibang')
    robot.login()
    robot.publish(00, "", '''小骆：''');
    #robot.reply(42, 9, " ", "小孩子越来越聪明")
    
    

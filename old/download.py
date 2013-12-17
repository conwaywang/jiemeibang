#encoding: utf-8
import time
import random
import urllib,urllib2

class Download(object):
    def __init__(self):
        self.headers={'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6)Gecko/20091201 Firefox/3.5.6',  'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}

    def get(self,url, encode="utf-8"):
        print "+",url
        content = urllib.urlopen(url).read().decode(encode, "ignore")
        #暂停
        time.sleep(random.uniform(3,6))
        return content
        '''
        req = urllib2.Request(url, None, self.headers)
        for i in range(3):
            try:
                temp = urllib2.urlopen(req)
                print chardet.detect(temp)
                if temp.getcode()==200:
                    if 'content-type' in temp.headers.keys():
                        content_type = temp.headers.get('content-type')
                        
                        if 'text' in content_type:
                            content = temp.read()
                            print content
                            temp.close()
                            return content
                        else:
                            content = temp.read()
                            temp.close()
                            return content
            except:
                continue
        '''
        

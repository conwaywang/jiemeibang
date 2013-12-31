#! /usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on 2013-12-19

@author: conway
'''
import ConfigParser
import os

class Conf(object):
    def __init__(self, confPath):
        if not os.path.exists(confPath):
            return
        self.confPath = confPath
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open( confPath , "r"))
        
    def __del__(self):
        self.config.write(open(self.confPath, "w"))  #回写到文件
    
    def get(self, section, key):
        return self.config.get(section, key)
    def set(self, section, key, value):
        self.config.set(section, key, value)
        

if __name__ == '__main__':
    conf = Conf("../conf/crawlerConf")
    #conf.set("xiachufang", "start", "7")
    
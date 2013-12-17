#encoding: utf-8

import MySQLdb

class MysqlConnector(object):
	def __init__(self):
		self.host = "localhost"
		self.user = "root"
		self.passwd = ""
		self.dbname = "startdb"
		
		#存储已下载url  字段 id url crawledtime
		self.table_crawledurl = "urllist"
		#存储下载的文章信息  id tile posttime postcontent fromsrc
		self.table_postinfo = "postinfo"
		
		#链接数据库
		self.conn = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd,db=self.dbname,use_unicode=1,charset="utf8")
		#self.conn.set_character_set("utf8")
		#初始化游标
		self.cursor = self.conn.cursor()
		self.cursor.execute("SET NAMES utf8")
		self.conn.commit()
		
	def __del__(self):
		if self.cursor:			
			self.cursor.close()
		if self.conn:
			self.conn.close()
	
	#判断url是否已下载。在下载表中
	def isURLDownload(self, url):
		sql = "select * from " + self.table_crawledurl + " where url='" + url + "'"
		#print sql
		count = self.cursor.execute(sql)
		
		return count
	 
	#添加url到已下载表中
	def addURL2Download(self, url):
		sql = "insert into " + self.table_crawledurl + "(url,crawledtime)values('"+url+"',NOW())"
		#print sql
		self.cursor.execute(sql)
		self.conn.commit()
		
	#添加文章信息到数据表中
	def addPost2PostInfo(self, title, time, url, text, src):
		sql = "insert into " + self.table_postinfo + "(title,posttime,posturl,postcontent,fromsrc)values('"+\
			MySQLdb.escape_string(title.encode("utf-8"))+"','"+time+"','"+url+"','"+\
			MySQLdb.escape_string(text.encode("utf-8"))+"','"+src+"')"
		#print sql
		ret = self.cursor.execute(sql)
		self.conn.commit()
		
		return ret
	
	#从数据库中得到某个网站的标题信息集合
	def getTitles(self, url):
		title_list = []
		sql = "select title from "+ self.table_postinfo + " where fromsrc='"+url+"'"
		self.cursor.execute(sql)	
		for i in self.cursor.fetchall():
			title_list.append(i)
			
		return title_list
	
	#得到某个网站的已下载url集合
	def getUrls(self, domain):
		url_list = []
		sql = "select posturl from "+ self.table_postinfo + " where fromsrc='"+domain+"'"
		self.cursor.execute(sql)	
		for i in self.cursor.fetchall():
			url_list.append(i)
			
		return url_list
	
	#删除某天的数据
	def delete_date(self, start_time):
		sql = "delete from urllist where crawledtime>\"%s\"" % (start_time)
		print sql
		self.cursor.execute(sql)
		
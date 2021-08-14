# -*- codeing: utf-8 -*-

'''
1、获取其实地址的页面内容，解释出“书名，书的地址”
2、根据书的地址，获取书的详细信息
3、根据书的地址，获得章节目录，获取章节标题和章节地址
4、根据章节地址，获得章节内容，上一章和下一章

数据处理
 把书的信息提交数据库，获得书的本地mhid
 根据书的封面原始地址和本地mhid，下载并保存书的封面

 处理每一章，保持章节的mhid与书的mhid的一致性。
 章节的ji_no章节id处理。
 处理章节内容，解析出每一章的图片地址，下载图片
 完成下载后，修改章节内容中的图片地址链接

 把下载图片按封面和章节内容，分别提交到服务器
 把书信息提交到服务器，创建书
 把章节内容提交到服务器，创建每个章节，或者修改章节的内容使得图片可以在本站显示
'''
# here put the import lib

import base64
import json
import os
import re
import socket
import threading
import time
import bs4
import requests
import random

from Common.Lib.fakePhoneAgent import getPhoneUserAgent
from Common.facation import * 
from Common.hmAnalysis import * 
from Common.mkzAnalysis import *
from lxml import etree, html

from Conf.config import *
from Common.Lib.DB import *
from Common.functions import *

from celery import Celery






#threads = []
# thread类
# class myThread (threading.Thread):
#     def __init__(self, page_filename, page_url):
#         threading.Thread.__init__(self)
#         self.page_filename = page_filename
#         self.page_url = page_url
#     def run(self):
#         spider.save_image(self.page_filename, self.page_url) # 多线程保存图片





class Spider(Facation):
    def __init__(self, word):
        super().__init__()
        print(word)
        self.url_book = []
        self.url_cpt  = []
        self.url_list = []
        self.word = word
        self.reg_analysis(mkzAnalysis())
        self.reg_analysis(hmAnalysis())
        self.db = DB.getdatebase()

    #
    def addRowbook(self,start_url,burl,bname,bcover):
        #做一个已经采集过的书的列表，避免重复存数据库
        if self.url_book is None or 0 == len(self.url_book):
            self.url_book = []
            ls = self.db.M('vv_sh_mhlist').fields(['url_org']).where ( " 1 ").fetchall()
            for li in ls:
                self.url_book.append(li[0])

        mhid = re.search('\d+',burl).group()

        host = get_host(start_url)        
        if burl.startswith('/'):
            burl = host + burl
        if bcover.startswith('/'):
            bcover = host + bcover
        
        if burl in self.url_book:
            print("已经采集过"+burl)
            return 

        self.db.M('vv_sh_mhlist').save({
            'url_org':burl,
            'title':bname,
            'cover_pic_org':bcover,
            'mhid_org':mhid,
            'mhid':mhid, #暂时让mhid=mhid_org
            'create_time':NOW,
            'statu':1

        })

        #self.db.addRowBook(burl,bname,bcover)

    #从输入的url列表中一一搜索
    def searchbooks(self,urllist):
        for url in urllist:
            self.searchbook(url)

    #仅搜索一个地址
    def searchbook(self,start_url):
    #    print("searchbook {}".format(start_url))
        print(headers)
        
        als = self.get_analysis(start_url)
        print (als._jobname)
        als.searchbook(start_url)
        return 

   
    def save_book(self,comic_url,bookinfo):
        result = self.db.M('vv_sh_mhlist').where({'url_org':comic_url}).save(bookinfo)
        return result
    
    def add_row_chapt(self,comic_id,cptid,cptname,cpturl ):
        #做一个已经采集过的列表，避免重复采集
        if self.url_cpt is None or 0 == len(self.url_cpt) :
           self.url_cpt = []
           ls = self.db.M('vv_sh_episodes').fields(['url_org']).where("`mhid` = {}".format(comic_id)).fetchall()
           for li in ls:
               self.url_cpt.append(li[0])

        if cpturl in self.url_cpt:
            print ("已经采集过"+cpturl)
            return    

    

        result = self.db.M('vv_sh_episodes').save({
            'mhid':comic_id,
            'ji_no':cptid,
            'title':cptname,
            'url_org':cpturl,
            'statu':0,
            'create_time':NOW
        })

        self.url_cpt.append(cpturl)
        return result 

    def save_chapt(self,cpturl,chaptinfo):
        result = self.db.M('vv_sh_episodes').where({'url_org':cpturl}).save(chaptinfo)
        return result
    
    
    #获得一本漫画的详情     
    def search_book_detail(self,comic_id,comic_url,notify=None):
        als = self.get_analysis(comic_url)
        print (als._jobname)
        als.search_book_detail(comic_id,comic_url,notify)
        return 

    def search_chapt_detail(self,bid,cptid,cpturl):
        als = self.get_analysis(cpturl)
        print (als._jobname)
        als.search_chapt_detail(bid,cptid,cpturl)
        return 


    #单纯地下载，把url保存到本地savename文件，只处理网络出错。如果目录不存在等等，都不管。
    #成功返回True，失败记录日志，并返回False
    def download(self,url,savename):
        #判断文件是否存在，如果存在就不再下载直接返回urlname
        if os.path.exists(savename):
            print("跳过",url)
            return True
        
        self.prepare_path(savename)
        #开始下载,成功返回新地址，失败返回原地址
        try:
            print("{} => {}".format(url,savename))

            pic = requests.get(url,headers=headers)
            fp = open(savename, 'wb')
            fp.write(pic.content)
            fp.close()
            return True
        except requests.exceptions.ConnectionError:
            print('下载失败，请检查源地址:{}.'.format(url))
            #记录下载错误的文件，可以以后重新下载。
            errorlog(2,1,"{} , {}".format( url,savename)) 
            
            return False
    
        return  True

    #检查文件中包含的目录，如果目录不存在，就mkdir
    #filepathname 类似 "/dir/file.ext"这种结构的带文件名的字符串
    def prepare_path(self,filepathname):
        #小心斜杠，有的是/有的是\，统一弄成/
        filepathname = filepathname.replace('\\','/')
        pathname = os.path.dirname(filepathname)
        pathlist = pathname.split('/')
        #print(pathlist)
        ph = ""
        
        while 0 < len(pathlist):
            l = pathlist.pop(0)
            ph = ph + l+'/'
            #print(ph)
            if not os.path.isdir(ph):
                os.mkdir(ph)
          
        return 


    #按照给定的设置，下载章节中的一个图片。
    #picPath 本地保存下载文件的根目录 下载后的文件名为 picPath/mhid/chpid/file
    #rooturl 外部访问下载文件的根目录，访问如下地址可以访问到下载的文件 rooturl/mhid/chpid/file
    #url 原始地址，从原始地址下载，保存到本地picPath/mhid/chpid/file ，从外部可以访问到
    #mhid chpid 书的id和章节id
    #这个函数可以用来下载封面，把chpid用""空字符串替代即可。保存的picPath另外指定。url用封面的原始地址
    def pre_download_cpt_pic(self,picPath,rooturl,url, mhid,chpid):
        #依次建立目录
        path = picPath
        #if not os.path.isdir(path):
        #    os.mkdir(path)
            
        path = picPath+'/' + str(mhid)
        #if not os.path.isdir(path):
        #    os.mkdir(path)
            
        path = picPath+'/' + str(mhid)+'/' + str(chpid)
        #if not os.path.isdir(path):
        #    os.mkdir(path)
        
        
        #按原文件名，存储在 picPath/mhid/cpid/
        filename = os.path.basename(url).split('!')[0]
        savename = path+'/' +filename
        urlname  = rooturl+'/' + str(mhid)+'/' + str(chpid)+'/' +filename
        
        if url not in self.url_list :
            self.db.M('vv_sh_download').save({
                'mhid':mhid,
                'ji_no':chpid,
                'url_org':url,
                'url':urlname,
                'pathname':savename
            }) 

        # ok = self.download(url,savename)
        
        # if True == ok :
        #     return urlname 
        # else :
        #     self.db.M('vv_sh_download').where({'mhid':mhid,'ji_no':chpid}).save({                
        #         'url':urlname,
        #         'pathname':savename
        #     }) 
        return urlname

    def setTofile(self,mhid,cpid,pics):
        fname = "./ok_"+ time.strftime("%Y-%m-%d_%H", time.localtime())+".txt"
        fp=open(fname,"a+")
        fp.write("UPDATE  `vv_mh_episodes` SET pics ='{}' WHERE mhid = {} AND ji_no ={};\r\n".format(pics,mhid,cpid) );
        fp.close()
        return

    def save_2_date(self,mhid,cpid,pics):
        self.db.M('vv_sh_episodes').where({'mhid':mhid,'ji_no':cpid}).save({
               'pics_local':pics,
               'statu':2
            })      
        
        return  
    def save_2_cover(self,mhid,coverfilename):
        self.db.M('vv_sh_mhlist').where({'mhid':mhid}).save({
            'cover_pic':coverfilename
        })
        return
    def get_book_cover(self,mhid):
        data = self.db.M('vv_sh_mhlist').fields(['mhid','cover_pic_org']).where({'mhid':mhid}).fetchone()
        return data
    def get_book_pics(self,mhid):
        data = self.db.M('vv_sh_episodes').fields(['mhid','ji_no','pics']).where({'mhid':mhid,'statu':1}).fetchall()
        return data

    def prepare_download(self,mhid):
        self.url_list = []
        downloadlist = self.db.M('vv_sh_download').fields(['url_org']).where({'mhid':mhid}).fetchall()
        for l in downloadlist:
           self.url_list.append(l[0])
        return

    def pre_download_book_cover(self,bid,root_path,root_url):       

        #先把封面图片的下载信息加入下载表
        data = self.get_book_cover(bid)
        curl = data[1]

        if curl not in self.url_list :
            filename = self.pre_download_cpt_pic(root_path,root_url,curl,bid,0)
            filename = root_url+'/'+bid+"cover.jpg" #用这个目录，与自己网站的规则保持一致。
            self.save_2_cover(bid,filename)

        return

    def pre_download_book_chapt(self,bid,root_path,root_url):      
        data = self.get_book_pics(bid)
        for row in data:
            print("漫画id={}    章节id={}".format(row[0],row[1]))
            lines = row[2].split(',') #先拆开，每个图片一行
            pics = ""
            for url in lines:
                #line = line.split('!')[0] #去掉!后面的部分 不要再这里拆，下载需要这个参数做验证
                pics = pics +  self.pre_download_cpt_pic(root_path,root_url,url,row[0],row[1]) + ","
                #print (pics)
            pics = pics.rstrip(',')
            print(pics)
            self.save_2_date(row[0],row[1],pics)
        
        return
        



if __name__ == "__main__":  
    spider = Spider("现在开始\r\n")
    #spider.searchbook("http://www.ikanwzd.top/booklist")  #检查是否有新书
    #spider.searchbook("https://www.mkzhan.com/top/popularity/")
    #spider.search_book_detail(215599,"https://www.mkzhan.com/215599/")
    spider.search_chapt_detail(215599,901869,"https://m.mkzhan.com/215897/933503.html")
  #  spider.prepare_path("/x/2x/3x/4x/66.txt")
  #  spider.prepare_path("./x/2x/3x/4x/66.txt")
"""     db = DB.getdatebase() 
    
    blist =db.M('vv_sh_mhlist').fields(['id','mhid_org','title','url_org']).where(' 1 ').fetchall()
    #检查每一本书是否有更新，是否有新章节
    
    for book in blist:
        spider.search_book_detail(book[1],book[3])
        spider.prepare_download(book[1])
        spider.pre_download_book_cover(book[1],rootcover,rootcoverurl)
        spider.pre_download_book_chapt(book[1],rootpic,rooturl)
    
    for book in blist:
        dlist = db.M('vv_sh_download').fields(['url_org','pathname']).where({'statu':0,'mhid':book[1]}).fetchall()
        for d in dlist:
            print(d)
            url = d[0]
            savename = d[1] 
            ok = spider.download(url,savename)
        
            if True == ok :
                db.M('vv_sh_download').where({'url_org':url}).save({                
                    'statu':1
                }) """







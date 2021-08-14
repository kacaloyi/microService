# -*- coding: UTF-8 -*-  
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

#pip install opencc-python-reimplemented

from opencc import OpenCC 
from Common.functions import *
from Common.facation  import * 


class hmAnalysis(Analysis):
    def __init__(self):
        Analysis.__init__(self,"ikanwzd")
        return

#仅搜索一个地址
    def searchbook(self,start_url):
        print("searchbook {}".format(start_url))
        
        try:
            response = requests.get(start_url, headers=headers)
            
        except requests.RequestException as e:
            print (e)
            #print ("状态码：",r.status_code)
            #print ("网站源代码",r.text)
            #print ("头部请求",r.headers) 
            return
        else:

            myhtml = etree.HTML(response.content.decode())

            ul = myhtml.xpath("//ul[@class = 'manga-list-2']/li")
        
            for li in ul:
                bname = li.xpath("./p[@class ='manga-list-2-title']/a/text()")[0] #xpath出来的是个 list 对象。
                burl  = li.xpath("./p[@class ='manga-list-2-title']/a/@href")[0]
                bcover = li.xpath("./div/a/img/@data-original")[0]
                print(bname,": ",burl,"封面:",bcover)
                self.get_Facation().addRowbook(start_url,burl,bname,bcover)

#获得一本漫画的详情     
    def search_book_detail(self,comic_id,comic_url,notify=None):
        print('search_book_detail {} {}'.format(comic_id,comic_url))
        try:
            if None != notify :
                notify.update_state(state='PROGRESS',	
                          meta={'current': 0, 'total': 1,	
                                'status': "get url"+comic_url})	
            response = requests.get(comic_url, headers=headers)
            
        except requests.RequestException as e:
            print (e)
            errorlog(1,2,e)
            return
        else:
            myhtml = etree.HTML(response.content.decode())
            bname = myhtml.xpath("//span[@class = 'normal-top-title']/text()") 
            bname = bname[0] if 0< len(bname) else ""
            binfo = myhtml.xpath("//p[@class ='detail-main-info-author']") #这个有一组，第一个是别名，第二个是作者名
            
            bbname   = binfo[0].xpath("./a/text()")
            bbname   = bbname[0] if 0< len(bbname) else ""              
            bauthor  = binfo[1].xpath("./a/text()")   #作者名
            bauthor  = bauthor[0] if 0< len(bauthor) else ""
            bzone   = binfo[2].xpath("./a/text()")   #地区，韩国
            bzone   = bzone[0] if 0< len(bzone) else ""
            #bbname  = bbname[0]  #书的别名
            bcoverpic = myhtml.xpath("//div[@class='detail-main-cover']/img/@data-original")
            bcoverpic = bcoverpic[0] if 0< len(bcoverpic) else ""

            bcate   = myhtml.xpath("//p[@class ='detail-main-info-class']/span/a/text()")   #书的分类，都市什么的
            bcate   = bcate[0] if 0< len(bcate) else ""
            bsummery = myhtml.xpath("//p[@class ='detail-desc']/text()")
            bsummery = "" if len(bsummery)==0  else bsummery[0] 
            

            bstate       = myhtml.xpath("//div[@id='detail-list-title']/span[@class='detail-list-title-1']/text()")[0]  #连载完结
            bupdate_time = myhtml.xpath("//div[@id='detail-list-title']/span[@class='detail-list-title-3']/text()")[0] #‘xxxx-xx-xx更新‘更新时间
            bupdate_time = re.search("\d+\-?\d{2}-?\d{2}",bupdate_time).group() #‘xxxx-xx-xx更新‘只取时间，忽略掉后面的

            #繁简转换
            bname = OpenCC('t2s').convert(bname)
            bbname = OpenCC('t2s').convert(bbname)
            bauthor = OpenCC('t2s').convert(bauthor)
            bsummery = OpenCC('t2s').convert(bsummery)
            print(bname)
            print(bbname)
            print(bauthor)
            print(bzone)
            print(bcate)
            print(bstate)
            print(bupdate_time)
            print(bcoverpic)
            print(bsummery)
            if None != notify :
                notify.update_state(state='PROGRESS',	
                          meta={'current': 0, 'total': 1,	
                                'status': "save_book"+comic_url})	

            self.get_Facation().save_book(comic_url,
                {
                    'mhid':comic_id,
                    'statu':1, # 0 刚建立 1详情已经获得 2封面已经下载
                    'state':get_book_state(bstate),
                    'title':bname,
                    'create_time':NOW,
                    'cover_pic_org':bcoverpic,
                    'mhcate':get_book_mhcate(bcate),
                    'cateids':get_book_cate(bcate),
                    'author':bauthor,
                    'summary':bsummery,
                    'episodes':0
                }
            )
            

           

            bchapts = myhtml.xpath("//ul[@id = 'detail-list-select']/li")
            self.url_cpt = []
            i = 0
            for cpt in bchapts:
                cptname = cpt.xpath("./a/text()")
                cptname = cptname[0]  if 0< len(cptname) else "无标题"
                cpturl  = cpt.xpath("./a/@href")[0] #chapter/19751
                cptid = re.search("\d+",cpturl).group() #匹配到第一个整数
                if  cpturl.startswith('/'):
                    host = get_host(comic_url)
                    cpturl = host+cpturl 
                
                
                if None != notify :
                    notify.update_state(state='PROGRESS',	
                          meta={'current': i, 'total': len(bchapts),	
                                'status': cptname })
                i= i+1	
                print(comic_id," ",cptid," ",cptname," ",cpturl)
                self.get_Facation().add_row_chapt(comic_id,cptid,cptname,cpturl )

    def getBookChaptList():
        return

    def search_chapt_detail(self,bid,cptid,cpturl):
        print("search_chapt_detail {} {} {} ".format(bid,cptid,cpturl))
        try:
            response = requests.get(cpturl, headers=headers)
            
        except requests.RequestException as e:
            print (e)
            errorlog(1,2,e)
            return
        else:
            myhtml = etree.HTML(response.content.decode())
            bbar = myhtml.xpath("//ul[@class='view-bottom-bar']/li")
            ppage = bbar[0].xpath("./a/@href")[0]
            npage = bbar[1].xpath("./a/@href")[0]

            pcpt_id = re.search("\d+",ppage).group()
            ncpt_id = re.search("\d+",npage).group()

            imgs = myhtml.xpath("//div[@id = 'cp_img']/img")
            info = ""
            for img in imgs:
                picurl = img.xpath("./@data-original")[0]
                print (picurl)
                info = info + picurl + ','
            info = info.rstrip(',')
            print(info)

            print("上一章:"+ppage+" 章节id:"+pcpt_id)
            print("下一章:"+npage+" 章节id:"+ncpt_id)
            self.get_Facation().save_chapt(cpturl,{
                'mhid':bid,
                'ji_no':cptid,
                'pics':info,
                'pji_no':pcpt_id,
                'nji_no':ncpt_id,
                'statu':1
            })

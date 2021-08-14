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


from Common.functions import *
from Common.facation  import * 


class mkzAnalysis(Analysis):

    def __init__(self):
        Analysis.__init__(self,"mkzhan")
        return
#仅搜索一个地址
    def searchbook(self,start_url):
        print("searchbook {}".format(start_url))
        #https://comic.mkzcdn.com/top/ticket/?page_num=3&page_size=20&type=2 获取JSON列表。
        try:
            response = requests.get(start_url)#, headers=headers)
            
        except requests.RequestException as e:
            print (e)
            #print ("状态码：",r.status_code)
            #print ("网站源代码",r.text)
            #print ("头部请求",r.headers) 
            return
        else:

            myhtml = etree.HTML(response.content.decode())

            ul = myhtml.xpath("//div[@class = 'top-list__box clearfix']/div[@class ='top-list__box-item' ]")
        
            for li in ul:
                bname = li.xpath("./p[@class ='comic__title']/a/text()")[0] #xpath出来的是个 list 对象。
                burl  = li.xpath("./p[@class ='comic__title']/a/@href")[0]
                bcover = li.xpath("./a/img/@data-src")[0]
                print(bname,": ",burl,"封面:",bcover)
                #self.get_Facation().addRowbook(start_url,burl,bname,bcover)

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
            binfo = myhtml.xpath("//div[@class ='de-info__box']")[0] #一组内容

            bname = binfo.xpath("./p[@class = 'comic-title j-comic-title']/text()")[0]                
            bbname   = bname# binfo.xpath("./a/text()")          
            bauthor  = binfo.xpath("./div[@class ='comic-author']/span[@class='name']/a/text()")[0]   #作者名
            bzone   = 2  #地区，中国内地

            #bbname  = bbname[0]  #书的别名
            bcoverpic = binfo.xpath("./div[@class='de-info__cover']/img/@data-src")[0]

            bcatenode   = binfo.xpath("./div[@class ='comic-status']/span")[0]
            bcate   = bcatenode.xpath("./b/text()")[0]    #书的分类，都市什么的
            bcate  = bcate.replace(' ','|')  #分割符号从空格换成|

            bsummery = binfo.xpath("./div[@class='comic-intro']/p[@class ='intro']/text()")[0]
            bsummery = bsummery.strip()
            

            bstatenode       = myhtml.xpath("//div[@class='de-chapter__title']/span")[0]  #连载完结
            bstate = bstatenode.xpath("./text()")[0]

            bupdate_time_node = myhtml.xpath("//div[@class='de-chapter__title']/span")[1] #‘xxxx-xx-xx更新‘更新时间
            bupdate_time = bupdate_time_node.xpath("./text()")[0]
            bupdate_time = re.search("\d+\.?\d{2}.?\d{2}",bupdate_time).group() #‘xxxx-xx-xx更新‘只取时间，忽略掉后面的
            bupdate_time = bupdate_time.replace('.','-')

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

            # self.get_Facation().save_book(comic_url,
            #     {
            #         'mhid':comic_id,
            #         'statu':1, # 0 刚建立 1详情已经获得 2封面已经下载
            #         'state':get_book_state(bstate),
            #         'title':bname,
            #         'create_time':NOW,
            #         'cover_pic_org':bcoverpic,
            #         'mhcate':get_book_mhcate(bcate),
            #         'cateids':get_book_cate(bcate),
            #         'author':bauthor,
            #         'summary':bsummery,
            #         'episodes':0
            #     }
            # )
            

           

            bchapts = myhtml.xpath("//ul[@class = 'chapter__list-box clearfix hide']/li")
            self.url_cpt = []
            i = 0
            for cpt in bchapts:
                cptname = cpt.xpath("./a/text()")
                cptname = "".join(cptname).strip()
                cpturl  = cpt.xpath("./a/@data-hreflink")[0] #chapter/19751
                cptid = cpt.xpath("./a/@data-chapterid")[0] #匹配到第一个整数
                if  cpturl.startswith('/'):
                    host = get_host(comic_url)
                    cpturl = host+cpturl 
                
                
                if None != notify :
                    notify.update_state(state='PROGRESS',	
                          meta={'current': i, 'total': len(bchapts),	
                                'status': cptname })
                i= i+1	
                print(comic_id,cptid,cptname,cpturl)
            #    self.get_Facation().add_row_chapt(comic_id,cptid,cptname,cpturl )

    def getBookChaptList():
        return

    #https://comic.mkzcdn.com/chapter/content/v1/?chapter_id=934027&comic_id=215897&format=1&quality=1
    #本来还有个sige，但是好像没有也没有关系。后面试试再说。
    #format取值范围0/1，qulity取值范围1/2/3数值越大，图片越大。
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
            #bbar = myhtml.xpath("//div[@class='rd-aside']")[0]
           
            # ppage = bbar.xpath("./a[@class ='rd-aside__item j-rd-prev']")[0]
            # print(etree.tostring(ppage))
            # return
            # npage = bbar.xpath("./a[@class ='rd-aside__item j-rd-next']/@href")

            # pcpt_id = re.search("\d+",ppage).group()
            # ncpt_id = re.search("\d+",npage).group()

            #imgs = myhtml.xpath("//div[@id = 'pages-tpl']/div")
            #分成几段动态加载的。刚开始只有ul，后来加载的li
            imgs = myhtml.xpath("//ul[@class = 'comic-list']/li[@class = 'comic-page']")
            print(imgs)
            info = ""
            for img in imgs:
                #picurl = img.xpath("./img/@data-src")[0]
                picurl = img.xpath("./img/@src")[0]
                print (picurl)
                info = info + picurl + ','
            info = info.rstrip(',')
            #print(info)

            # print("上一章:"+ppage+" 章节id:"+pcpt_id)
            # print("下一章:"+npage+" 章节id:"+ncpt_id)
          
            # self.get_Facation().save_chapt(cpturl,{
            #     'mhid':bid,
            #     'ji_no':cptid,
            #     'pics':info,
            #     'pji_no':pcpt_id,
            #     'nji_no':ncpt_id,
            #     'statu':1
            # })

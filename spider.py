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
from lxml import etree, html

from Conf.config import *
from Common.Lib.DB import *
from Common.functions import *

from celery import Celery


# 将两个列表对应组和成一个新的字典
def list2dic(list1,list2):
    # lambda是匿名函数, 冒号前为参数, 后面为返回值, 即传入x, y, 返回[x,y]
    # map函数, 第一个参数为函数名, 后面为参数, 返回返回一个将 function 应用于 iterable 中每一项并输出其结果的迭代器。
    return dict(map(lambda x,y:[x,y], list1,list2)) 

# 起始位置，漫画的全部列表页面
base_url = [
    
     "http://www.ikanwzd.top/booklist",
     "http://www.ikanwzd.top/booklist?page=2",
     "http://www.ikanwzd.top/booklist?page=3",
     "http://www.ikanwzd.top/booklist?page=4",
     "http://www.ikanwzd.top/booklist?page=5",
     "http://www.ikanwzd.top/booklist?page=6",
     "http://www.ikanwzd.top/booklist?page=7",
     "http://www.ikanwzd.top/booklist?page=8",
     "http://www.ikanwzd.top/booklist?page=9",
     "http://www.ikanwzd.top/booklist?page=10",
     "http://www.ikanwzd.top/booklist?page=11",
     "http://www.ikanwzd.top/booklist?page=12",
     "http://www.ikanwzd.top/booklist?page=13",
     "http://www.ikanwzd.top/booklist?page=14"

]



# ip池
proxies_list = [
    'http://42.3.51.114:80',
    'http://39.106.205.147:8085',
    'http://220.135.8.49:40297',
    'http://47.52.231.140:8080',
    'http://183.166.97.173:999',
    'http://117.59.224.64:80',
    'http://103.220.73.39:8080',
    'http://150.138.253.71:808',
    'http://118.25.35.202:9999',
    'http://221.2.155.35:8060',
    'http://119.254.94.93:8088',
]

# 随机代理与请求头
proxies = {'http': random.choice(proxies_list)}
headers = {"User-Agent": getPhoneUserAgent()}



#threads = []
# thread类
# class myThread (threading.Thread):
#     def __init__(self, page_filename, page_url):
#         threading.Thread.__init__(self)
#         self.page_filename = page_filename
#         self.page_url = page_url
#     def run(self):
#         spider.save_image(self.page_filename, self.page_url) # 多线程保存图片





class Spider:
    def __init__(self, word):
        print(word)
        self.url_book = []
        self.url_cpt  = []
        self.url_list = []
        self.word = word
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
        print("searchbook {}".format(start_url))
        print(headers)
        
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
                self.addRowbook(start_url,burl,bname,bcover)
    
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

            self.save_book(comic_url,
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
                self.add_row_chapt(comic_id,cptid,cptname,cpturl )


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
            self.save_chapt(cpturl,{
                'mhid':bid,
                'ji_no':cptid,
                'pics':info,
                'pji_no':pcpt_id,
                'nji_no':ncpt_id,
                'statu':1
            })


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
  # spider.searchbooks(base_url)  #检查是否有新书
    spider.prepare_path("/x/2x/3x/4x/66.txt")
    spider.prepare_path("./x/2x/3x/4x/66.txt")
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







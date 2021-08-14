# -*- coding: UTF-8 -*-  
'''
class Button(object):
   html = ""
   def get_html(self):
      return self.html

class Image(Button):
   html = "<img></img>"

class Input(Button):
   html = "<input></input>"

class Flash(Button):
   html = "<obj></obj>"

class ButtonFactory():
   def create_button(self, typ):
      targetclass = typ.capitalize()
      return globals()[targetclass]()

button_obj = ButtonFactory()
button = ['image', 'input', 'flash']
for b in button:
   print button_obj.create_button(b).get_html()
   

'''
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

class Analysis(object):

    #共同的facation，提供基本的工具函数save等等。
    _facation  = None
    _jobname   = ""

    def __init__(self,jobname):
        self._jobname = jobname
        return

    #根据url或者其它的关键字，判断是不是自己能做的任务。
    #jobname一般是个url。比如送入的是https://www.baidu.com/dodo.html等 ，本身的_jobname="baidu"，表明自己是处理百度任务的，而送入的url中有baidu字样，那么就可以处理，返回true;
    def is_myjob(self,jobname):
        if self._jobname in jobname :
            return True

        return False

    def set_Facation(self,facation):
        self._facation = facation
        return

    def get_Facation(self):
        return self._facation
    
    #仅搜索一个地址
    def searchbook(self,start_url):
        print("子类必须实现这个接口")
        return

#获得一本漫画的详情     
    def search_book_detail(self,comic_id,comic_url,notify=None):
        print("子类必须实现这个接口")
        return

    def getBookChaptList():
        return

    def search_chapt_detail(self,bid,cptid,cpturl):
        print("子类必须实现这个接口")
        return


class Facation(object):
    _analysis_array= []

    def __init__(self):
        self._analysis_array= []
        return

    def reg_analysis(self,analysis):
        self._analysis_array.append(analysis)
        analysis.set_Facation(self)
        return

    def get_analysis(self,jobname):
        for a in self._analysis_array:
            if True == a.is_myjob(jobname):
                return a
        return None

    def save_book(self,comic_url,bookinfo):
        print(comic_url,bookinfo)
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
        return
    def add_row_chapt(self,comic_id,cptid,cptname,cpturl ):
        print("add row chapter ",comic_id,cptid,cptname,cpturl)
        return

    def save_chapt(self,cpturl,cptinfo):
        print("add detail chapter ",cpturl,cptinfo)
            # {
            #     'mhid':bid,
            #     'ji_no':cptid,
            #     'pics':info,
            #     'pji_no':pcpt_id,
            #     'nji_no':ncpt_id,
            #     'statu':1
            # })
        return

    
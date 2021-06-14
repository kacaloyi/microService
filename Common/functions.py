# -*- codeing: utf-8 -*-
#一些共同的函数
import os 
import time 
import datetime

from urllib.parse import urlparse



NOW = int(time.time())

def dateformate(tvalue,format= "%Y-%m-%d %H:%M:%S"):
    struct_time = time.localtime(tvalue)  # 得到结构化时间格式
    f_time = time.strftime(format, struct_time)
    return f_time

def get_book_mhcate(bzone):
        bzone = bzone.strip()
        mcatelist = {
            '韩漫':'8' #日韩分类都是8 ，韩国漫画
        }
        mcatelist.setdefault(bzone,'5,6,7') #默认是正常漫画

        return mcatelist[bzone] 
        #return '5,6,7' 

def get_book_state(bstatu):
        bstatu = bstatu.strip()
        statulist = {
            '连载中': 1,
            '连载': 1,
            '已完结': 2,
            '完结': 2

        }
        statulist.setdefault(bstatu,1) #默认是连载中        
        return statulist[bstatu]

def get_book_cate(bcate):
        bcate = bcate.strip()
        catelist = {
            '玄幻':1 ,
            '仙侠':2, 
            '都市':3 ,
            '历史':4,
            '网游':5,
            '科幻':6,
            '灵异':7,
            '女频':8,
            '霸总':9,
            '恋爱':10,
            '校园':11,
            '冒险':12,
            '搞笑':13,
            '生活':14,
            '热血':15,
            '架空':16,
            '后宫':17,
            '耿美':18,
            '悬疑':19,
            '恐怖':20,
            '动作':21,
            '战争':22,
            '古风':23,
            '穿越':24,
            '竞技':25,
            '百合':26,
            '励志':27,
            '同人':28,
            '真人':29,
            '剧情':30,
            '萝莉':31,
            '都市':32
        }
        catelist.setdefault(bcate,32)
        return catelist[bcate]

def  get_host(url_path):
        parsed_url = urlparse(url_path)
        #ParseResult(scheme='https', netloc='docs.google.com', path='/spreadsheet/ccc', params='', query='key=blah-blah-blah-blah', fragment='gid=1')
        host = "{}://{}".format(parsed_url.scheme,parsed_url.netloc)
        return host
#level 错误等级
#errorno 错误类型代号
#message 错误信息
def errorlog(level,errorno,message):
    fname = "./error_"+ time.strftime("%Y-%m-%d", time.localtime())+".txt"
    fp=open(fname,"a+")
    fp.write("{},{},{}\r\n".format(level,errorno,message) );
    fp.close()
    return
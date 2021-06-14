# -*- codeing: utf-8 -*-
from .spider import *

if __name__ == "__main__":  
    spider = Spider("现在开始\r\n")
    spider.searchbooks(base_url)  #检查是否有新书

    
    db = DB.getdatebase() 

    blist =db.M('vv_sh_mhlist').fields(['id','mhid_org','title','url_org']).where(' 1 ').fetchall()
    #检查每一本书是否有更新，是否有新章节
    for book in blist:
        spider.search_book_detail(book[1],book[3])

    for book in blist:
        bid = book[1]
        clist = db.M('vv_sh_episodes').fields(['id','mhid','ji_no','url_org']).where({
            'mhid':bid,
            'statu':0
        }).fetchall()
        for cpt in clist:
            spider.search_chapt_detail(cpt[1],cpt[2],cpt[3])
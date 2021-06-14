#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8

"""
a flask sample module
使用flask和Celery共同构架一个可以和前端交互的长时间任务系统。需要一个Redis配合。
https://blog.csdn.net/cainiao_python/article/details/100981146/?utm_term=flaskpython%E5%90%8E%E5%8F%B0%E6%89%A7%E8%A1%8C&utm_medium=distribute.pc_aggpage_search_result.none-task-blog-2~all~sobaiduweb~default-6-100981146&spm=3001.4430

原版的flash+Celery介绍在这里：
http://www.pythondoc.com/flask-celery/first.html
使用nanobar实现简单的进度条，js代码。
https://blog.csdn.net/shijiujiu33/article/details/85227653
进度条更详尽的介绍。
https://www.cnblogs.com/y114113/p/6289629.html

启动celery的方式在celery5.0之后改了。
$ celery --app=proj worker -l INFO 
$ celery -A proj   worker  -l INFO -Q hipri,lopri 
$ celery -A proj   worker --concurrency=4 
$ celery -A proj   worker --concurrency=1000 -P eventlet 
$ celery worker --autoscale=10,0

celery --app=HelloWorld worker -P eventlet -l INFO
celery --app=HelloWorld.celery worker -l INFO
在5.0以前原来是:
celery worker -A app.celery --loglevel=info 

举例：
celery -A app.celery_tasks.celery worker -Q queue --loglevel=info
主文件名是celery_tasks.py 
里面的worker函数用@
# -A参数指定创建的celery对象的位置，
#   该app.celery_tasks.celery指的是app包下面的celery_tasks.py模块的celery实例，
#   注意一定是初始化后的实例，后面加worker表示该实例就是任务执行者；
# -Q参数指的是该worker接收指定的队列的任务，这是为了当多个队列有不同的任务时可以独立；如果不设会接收所有的队列的任务；
# -l参数指定worker输出的日志级别；

"""
import json
import time
import random
import datetime
from datetime import datetime,timedelta
from concurrent.futures import ThreadPoolExecutor
from time import sleep

from flask import Flask, render_template, request, jsonify ,url_for,redirect
#from flask_cache import Cache
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

import logUtil

from celery import Celery
from Conf.config import *  
from Common.functions import *
from spider import *
#import spider 


executor = ThreadPoolExecutor(2)
app = Flask(__name__)  #初始化flask的app对象
app.config['result_backend'] = CELERY_RESULT_BACKEND
app.config['broker_url'] = CELERY_BROKER_URL
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=5)

celery = Celery(app.name,broker = app.config['result_backend'])
celery.conf.update(app.config)

logger = logUtil.FileLogger #初始化日志对象



# set route 
@app.route('/') #设置默认的helloworld路由
def index():  #编写\路由对应的方法
    return render_template('index.html',urls='\n'.join(base_url))
    #return 'Hello, World!'

# render_template search templates dir default
@app.route('/get.html') #设置/get.html路由
def get_html(): #编写/get.html路由的方法
    return render_template('get.html') #返回get.html触发的事件，详情请看templates文件夹下get.html的设计

@app.route('/post.html') #设置/post.html路由
def post_html(): #编写/post.html路由对应的方法
    return render_template('post.html') #返回post.html触发的事件，详情请看templates文件夹下post.html的设计

#定义/deal_request路由，其实看了templates的html你会发现，最后都是来调用这个路由对应的方法
@app.route('/deal_request', methods = ['GET', 'POST'])
def deal_request(): #编写/deal_request对应的方法
    if request.method == "GET":
        # get通过request.args.get("param_name","")形式获取参数值
        logger.info('a GET request')  #利用日志对象logger收集日志
        for key,value in request.args.items():
            logger.info('{key}:{value}'.format(key = key, value = value))   #利用日志对象logger收集日志html上出过来的key和walue
        get_params = json.dumps(request.args) #利用日志对象logger收集日志html上出过来的key和walue#利用日志对象logger收集日志html上出过来的key和walue
        return get_params #返回最终的处理参数
    elif request.method == "POST":
        # post通过request.form["param_name"]形式获取参数值
        logger.info('a POST request')  #利用日志对象logger收集日志
        for key,value in request.form.items():
            logger.info('{key}:{value}'.format(key = key, value = value)) #利用日志对象logger收集日志html上出过来的key和walue
        post_params = json.dumps(request.form) #利用日志对象logger收集日志html上出过来的表单form数据
        return post_params #返回最终组装的json串post_params
    else:
        logger.warn('a request is neither a GET nor a POST')

#搜寻到的所有书的列表
#@cache.cached(timeout=5, key_prefix='view_%s', unless=True)
@app.route('/books', methods = ['GET', 'POST'])
def books_list():
    lists = DB.getdatebase().M("vv_sh_mhlist").fields(['mhid','title','statu','from_unixtime(create_time)','url_org']).where("1").order("create_time ASC").fetchall()
    if lists is None:
        lists = ["没有找到相应的数据"]
    
    
    return render_template('listBooks.html',items=lists,where = "1")

#搜寻到的所有书的列表
#@cache.cached(timeout=5, key_prefix='view_%s', unless=True)
@app.route('/bookinfo', methods = ['GET', 'POST'])
def books_info():
    mhid = 0 
    if request.method == "GET":
        mhid = request.args.get("mhid")
    if request.method == "POST":
        mhid = request.form.get("mhid")
    
    wh = {'mhid':mhid }

    db = DB.getdatebase()
    info = db.M("vv_sh_mhlist").fields(['mhid','title','statu','cover_pic','author','summary','from_unixtime(create_time)','url_org']).where(wh).fetchone()
    if info is None:
        info = ["没有找到相应的数据"]

    lists = db.M("vv_sh_episodes").fields(['ji_no','title','statu','from_unixtime(create_time)','update_time','pics']).where(wh).order("ji_no ASC").fetchall()
    if lists is None:
        lists = ["没有找到相应的数据"]
    

    return render_template('listCpt.html',items=lists,info = info )

#搜寻到的所有书的列表

#@cache.cached(timeout=5, key_prefix='view_%s', unless=True)
@app.route('/bookEdit', methods = [ 'POST',])
def book_edit():
    mhid = request.form.get("mhid")
    url_org = request.form.get("url_org")
    title = request.form.get("title")
    author = request.form.get("author")
    cover_pic = request.form.get("cover_pic")
    summary = request.form.get("summary")

    db = DB.getdatebase()
    db.M("vv_sh_mhlist").where("url_org='"+url_org+"'").save({
        'mhid':mhid,
        'title':title,
        'author':author,
        'cover_pic':cover_pic,
        'summary':summary
        #'url_org'
        
    })

    return "ok"
    


@app.route('/bookfile', methods = ['GET', 'POST'])
def books_file_list():
    mhid = 0 
    ji_no = 0
    if request.method == "GET":
        mhid = request.args.get("mhid")
        ji_no = request.args.get("ji_no")
    if request.method == "POST":
        mhid = request.form.get("mhid")
        ji_no = request.form.get("ji_no")

    wh = {'mhid':mhid,'ji_no':ji_no }
    if 0==ji_no or None == ji_no:
         wh = {'mhid':mhid }

    db = DB.getdatebase()
    info = db.M("vv_sh_mhlist").fields(['mhid','title','statu','cover_pic','author','summary','from_unixtime(create_time)','url_org']).where("mhid="+mhid).fetchone()
    if info is None:
        info = ["没有找到相应的数据"]

    lists =db.M("vv_sh_download").fields(['mhid','ji_no','url_org','url','pathname','create_time']).where(wh).order("create_time ASC").fetchall()
    if lists is None:
        lists = ["没有找到相应的数据"]

    return render_template('listFile.html',items=lists,info = info)
@app.route('/addBook', methods = ['GET'])
def addBook(): #显示结果
    mhid = request.args.get("mhid")
    wh = {'mhid':mhid }
    info = DB.getdatebase().M("vv_sh_mhlist").fields([
        'mhid','title','cover_pic','author','summary','state','mhcate','cateids','mhid_org'
        ]).where(wh).fetchone()

    return render_template('addBook.html',info = info,postsite=addbookapi)

@app.route('/addChapt', methods = ['GET'])
def addChapt(): #显示结果
    mhid = request.args.get("mhid")
    ji_no = request.args.get("ji_no")

    wh = {'mhid':mhid }
    db = DB.getdatebase()
    binfo = db.M("vv_sh_mhlist").fields([
        'mhid','mhid_org','title','author'
        ]).where(wh).fetchone()


    wh = {'mhid':mhid,'ji_no':ji_no }    
    info = db.M("vv_sh_episodes").fields([
        'mhid','ji_no','title','pics_local'
        ]).where(wh).fetchone()
    

    return render_template('addChapt.html',binfo = binfo,info = info,postsite=addcptapi)

@app.route('/tools', methods = ['GET', 'POST'])
def result_list(): #显示结果
    if request.method == "GET":
        return render_template('tlists.html',where="1")
    
    params = request.form.items()
    table = request.form.get("M")
    fields = request.form.get("fields")
    where = request.form.get("where")
    order = request.form.get("order")

    if ""==fields :
        fields = ' * '

    lists = DB.getdatebase().M(table).fields(fields).where(where).order(order).fetchall()
    #lists = [table,fields,where,order]
    if lists is None:
        lists = ["没有找到相应的数据"]
    #return json.dumps(lists)
    return render_template('tlists.html',items=lists,table=table,fields=fields,where=where,order=order)
    # for key,value in request.form.items():
    #     logger.info('{key}:{value}'.format(key = key, value = value)) #利用日志对象logger收集日志html上出过来的key和walue
    # post_params = json.dumps(request.form) #利用日志对象logger收集日志html上出过来的表单form数据
    # return post_params #返回最终组装的json串post_params
def run_jobs_download():
    url = request.form.get("url")
    filename = request.form.get("filename")

    task = download.apply_async(args=[url,filename], countdown=1)
    return jsonify({ }), 203, { 'Location': url_for('taskstatus', task_id=task.id)}  

def run_jobs_downloadpics():
    mhid = request.form.get("mhid")
    ji_no = request.form.get("ji_no")

    task = downloadPics.apply_async(args=[mhid,ji_no], countdown=1)
    return jsonify({ }), 203, { 'Location': url_for('taskstatus', task_id=task.id)}  

def run_jobs_bookdetail():
    mhid = request.form.get("mhid")
    url  = request.form.get("url")

    task = searchBookDetail.apply_async(args=[mhid,url], countdown=1)
    return jsonify({ }), 203, { 'Location': url_for('taskstatus', task_id=task.id)}  

@app.route('/jobs',methods=['GET','POST'])
def run_jobs():
    if request.method != "POST":
        return jsonify({"错误的请求方式" })
    
    print("/jobs")

    cmd = request.form.get("cmd")
    if cmd=="bookdetail" :
        return run_jobs_bookdetail() 

    if cmd=="downloadpics" :
        return run_jobs_downloadpics() 

    if cmd=="download" :
        return run_jobs_download()


    #for key,value in request.form.items():
    #    print('{key}:{value}'.format(key = key, value = value))
    urls = request.form.get("urls")
    #现在得到的是字符串，还要转化成list，因为searchBookList需要的是list
    urls = urls.split('\n')
    task = searchBookList.apply_async(args=[urls,], countdown=1) #单独一个参数，后面要有逗号，这样才能变成list
    #task = long_task.apply_async(args=[1, 2], countdown=60)
    #task = long_task.delay()
    #task = long_task.apply_async()	
    
    # 返回 202，与Location头
    return jsonify({ }), 203, { 'Location': url_for('taskstatus', task_id=task.id)}
   


@app.route('/status/<task_id>')	
def taskstatus(task_id):	
    task = long_task.AsyncResult(task_id)	
    if task.state == 'PENDING': # 在等待	
        response = {	
            'state': task.state,	
            'current': 0,	
            'total': 1,	
            'status': '等待中...'	
        }	
    elif task.state != 'FAILURE': # 没有失败	
        response = {	
            'state': task.state, # 状态	
            # meta中的数据，通过task.info.get()可以获得	
            'current': task.info.get('current', 0), # 当前循环进度	
            'total': task.info.get('total', 1), # 总循环进度	
            'status': task.info.get('status', '')	
        }	
        if 'result' in task.info:	
            response['result'] = task.info['result']	
    else:	
        # 后端执行任务出现了一些问题	
        response = {	
            'state': task.state,	
            'current': 1,	
            'total': 1,	
            'status': str(task.info),  # 报错的具体异常	
        }	
    return jsonify(response)

@celery.task(bind=True)
def downloadCovers(self):
    worker = Spider("下载所有书的封面\r\n")
    blist =DB.getdatebase().M('vv_sh_mhlist').fields(['cover_pic_org','cover_pic']).where(' 1 ').fetchall()
    len = len(blist)

    return {'current': len, 'total': len, 'status': 'Task completed!',	
            'result': "下载任务完成"}

@celery.task(bind=True)
def download(self,url,savename):
    worker = Spider("下载图片\r\n")
    self.update_state(state='PROGRESS',	
                          meta={'current': 0, 'total': 1,	
                                'status': "下载"+url})	
    ok = worker.download(url,savename)

    return {'current': 1, 'total': 1, 'status': 'Task completed!',	
            'result': "下载任务完成"}


@celery.task(bind=True)
def downloadPics(self,comic_id,ji_no=None):
    worker = Spider("下载指定书的图片\r\n")
    whe = {'mhid':comic_id}
    if 0 == comic_id or None == comic_id:
        return {'current': 1, 'total': 1, 'status': 'FAILURE',	
            'result': "没有指定mhid"}
    
    if None != ji_no :
        whe = {'mhid':comic_id,'ji_no':ji_no}

    db = DB.getdatebase()
    dlist =db.M('vv_sh_download').fields(['url_org','pathname']).where(whe).fetchall()
    total = len(dlist)
    i = 0
    for d in dlist:
        print(d)
        url = d[0]
        savename = d[1] 
        self.update_state(state='PROGRESS',	
                          meta={'current': i, 'total': total,	
                                'status': "下载"+url})	
        ok = worker.download(url,savename)
        i= i+1
        if True == ok :
            db.M('vv_sh_download').where({'url_org':url}).save({                
                  'statu':2
                }) 

    return {'current': total, 'total': total, 'status': 'Task completed!',	
            'result': "下载任务完成"}


@celery.task(bind=True)
def  searchBookDetailAll(self,comic_id,comic_url):
    blist =DB.getdatebase().M('vv_sh_mhlist').fields(['id','mhid_org','title','url_org']).where(' 1 ').fetchall()
    #检查每一本书是否有更新，是否有新章节
    
    for book in blist:
       searchBookDetail(book[1],book[3])

    return {'current': 100, 'total': 100, 'status': 'Task completed!',	
            'result': "任务完成"}	



@celery.task(bind=True)
def  searchBookDetail(self,comic_id,comic_url):
    worker = Spider("书的详情和章节列表\r\n")
    #第一步 ，获取漫画详情，章节列表
    self.update_state(state='PROGRESS',	
                    meta={'current': 0, 'total': 1,	
                        'status': "访问"+comic_url})	
    worker.search_book_detail(comic_id,comic_url,self)

    #第二步，获取章节详情
    self.update_state(state='PROGRESS',	
                          meta={'current': 0, 'total': 1,	
                                'status': "获取章节详情"})	
    clist = DB.getdatebase().M('vv_sh_episodes').fields(['id','mhid','ji_no','url_org']).where({
            'mhid':comic_id,
            'statu':0
        }).fetchall()

    total = len(clist)
    i = 0
    for cpt in clist:
            self.update_state(state='PROGRESS',	
                          meta={'current': i, 'total': total,	
                                'status': "获取章节详情"+cpt[3]})
            worker.search_chapt_detail(cpt[1],cpt[2],cpt[3])
            i= i+1

    #第三步，收集需要下载的数据。
    worker.prepare_download(comic_id)
    worker.pre_download_book_cover(comic_id,rootcover,rootcoverurl)
    worker.pre_download_book_chapt(comic_id,rootpic,rooturl)
    self.update_state(state='PROGRESS',	
                          meta={'current': 10, 'total': 10,	
                                'status': "采集结束"})	

    return {'current': 100, 'total': 100, 'status': 'Task completed!',	
            'result': "任务完成"}	

@celery.task(bind=True)
def  searchBookList(self,urls):

    total = len(urls)
    worker = Spider("搜索书的地址\r\n")

    for i in range(total):
        self.update_state(state='PROGRESS',	
                          meta={'current': i, 'total': total,	
                                'status': urls[i]})	
        worker.searchbook(urls[i])



    return {'current': i+1, 'total': total, 'status': '完成任务',	
            'result': "<a href= '/books'>查看结果</a>"}	

@celery.task(bind=True)
def long_task(self):
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']	
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']	
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']	
    message = ''	
    total = random.randint(10, 50)	
    for i in range(total):	
        if not message or random.random() < 0.25:	
            # 随机的获取一些信息	
            message = '{0} {1} {2}...'.format(random.choice(verb),	
                                              random.choice(adjective),	
                                              random.choice(noun))	
        # 更新Celery任务状态	
        self.update_state(state='PROGRESS',	
                          meta={'current': i, 'total': total,	
                                'status': message})	
        time.sleep(1)	
    # 返回字典	
    return {'current': 100, 'total': 100, 'status': 'Task completed!',	
            'result': 42}	



if __name__ == '__main__':
    #app.run(port=5000) #直接启动
    #利用tornado启动程序
    port=5000
    http_server = HTTPServer(WSGIContainer(app)) #将api的初始化对应委托给tornado的HTTPServer
    http_server.listen(port) #监听端口
    #logger.info('Listening on {}'.format(port))
    IOLoop.instance().start() #启动微服务

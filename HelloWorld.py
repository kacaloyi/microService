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
from concurrent.futures import ThreadPoolExecutor
from time import sleep

from celery import Celery
from flask import Flask, render_template, request, jsonify ,url_for,redirect
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

import logUtil

from conf.config import *

executor = ThreadPoolExecutor(2)
app = Flask(__name__)  #初始化flask的app对象
app.config['result_backend'] = CELERY_RESULT_BACKEND
app.config['broker_url'] = CELERY_BROKER_URL

celery = Celery(app.name,broker = app.config['result_backend'])
celery.conf.update(app.config)

logger = logUtil.FileLogger #初始化日志对象

# set route 
@app.route('/') #设置默认的helloworld路由
def hello_world():  #编写\路由对应的方法
    return render_template('index.html')
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


@app.route('/jobs',methods=['GET','POST'])
def run_jobs():
    #task = long_task.apply_async(args=[1, 2], countdown=60)
    #task = long_task.delay()
    task = long_task.apply_async()	
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
            'status': 'Pending...'	
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
    logger.info('Listening on {}'.format(port))
    IOLoop.instance().start() #启动微服务

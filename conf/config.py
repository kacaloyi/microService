# -*- codeing: utf-8 -*-



DBhost  ="192.168.8.137"  #数据库地址
DBuser  ="pxs"            #数据库账号
DBpass  ="xs123456"       #数据库密码
DBbase  ='pxs'            #所使用的库

# rootpic = './iix'          #章节内容图片所使用的存储目录
# rooturl = '/Public/file/iix' #外部访问所使用的url目录

# rootcover = './iixcover'    #封面图片使用的本地存储目录
# rootcoverurl ='/Public/file/iixcover' #外部访问封面图片所使用的url目录

#redis与celery通信的地址
CELERY_BROKER_URL = 'redis://192.168.8.137:6379/0'
CELERY_RESULT_BACKEND = 'redis://192.168.8.137:6379/0'




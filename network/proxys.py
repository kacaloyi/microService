# -*- codeing: utf-8 -*-

import os
import random

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
def getProxy():
    return random.choice(proxies_list)


#测试代码
if __name__ == "__main__":
    proxy = getProxy()   
    print(proxy)
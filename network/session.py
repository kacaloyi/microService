# -*- codeing: utf-8 -*-
import datetime
import time
import logging
import re
from collections import defaultdict

import json
import pickle

import requests

import proxys 
from fakePhoneAgent import *


#from Common.functions import ensure_file_dir_exists

requests.packages.urllib3.disable_warnings()
'''
可以从源码对比request.request是基于上下文管理器做的自动关闭session，
而session.request基于http长连接sokcet，保留历史请求的状态，
这就对依赖于登陆状态的二次请求提供了很便利的途径，
基于token，可以借助python reflect也就是反射实现token读取，共享

'''

class SessionMgr(object):
    SESSION_INSTANCE = {}
    DEFAULT_HEADERS = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36')
    }
    COOKIES_KEYS = ['name', 'value', 'path', 'domain', 'secure']
    DEFAULT_VERIFY = False


    @classmethod
    def get_session(cls, site):
        if site not in cls.SESSION_INSTANCE:
            session = requests.Session()
            session.headers.update(cls.DEFAULT_HEADERS)
            session.verify = cls.DEFAULT_VERIFY
            cls.SESSION_INSTANCE[site] = session
        return cls.SESSION_INSTANCE[site]

    @classmethod
    def set_session(cls, site, session):
        cls.SESSION_INSTANCE[site] = session
        return session

    @classmethod
    def load_session(cls, site, path):
        with open(path, "rb") as f:
            session = pickle.load(f)
            assert isinstance(session, requests.Session)
            cls.set_session(site, session)
            return session

    @classmethod
    def export_session(cls, site, path):
        ensure_file_dir_exists(path)
        session = cls.get_session(site)
        with open(path, "wb") as f:
            pickle.dump(session, f)

    @classmethod
    def update_cookies(cls, site, cookies):
        session = cls.get_session(site=site)
        for cookie in cookies:
            data = {key: cookie.get(key) for key in cls.COOKIES_KEYS}
            session.cookies.set(**data)

    @classmethod
    def load_cookies(cls, site, path):
        with open(path) as f:
            cookies = json.load(f)
            cls.update_cookies(site=site, cookies=cookies)
        return cls.get_session(site=site)

    @classmethod
    def export_cookies(cls, site, path):
        cookies = cls.get_cookies(site)
        ensure_file_dir_exists(path)
        with open(path, 'w') as f:
            json.dump(cookies, f, indent=4)

    @classmethod
    def get_cookies(cls, site):
        cookies = []
        session = cls.get_session(site=site)
        for c in session.cookies:
            args = dict(vars(c).items())
            data = {key: args.get(key) for key in cls.COOKIES_KEYS}
            cookies.append(data)
        return cookies

    @classmethod
    def clear_cookies(cls, site):
        session = cls.get_session(site=site)
        session.cookies.clear_session_cookies()

    @classmethod
    def set_proxy(cls, site, proxy):
        session = cls.get_session(site)
        session.proxies = {
            'http': proxy,
            'https': proxy
        }

    @classmethod
    def get_proxy(cls, site):
        session = cls.get_session(site)
        return session.proxies.get('http')

    @classmethod
    def set_verify(cls, site, verify):
        session = cls.get_session(site)
        session.verify = verify

'''
# 通过设置user-agent，用来模拟移动设备
user_ag='MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; '+
    'CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1'

options.add_argument('user-agent=%s'%user_ag)



# 添加代理

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.webdriver import Options
from selenium.webdriver.chrome.webdriver import WebDriver

# 静态IP：102.23.1.105：2005

PROXY = "proxy_host:proxy:port"
chrome_option = Options()
desired_capabilities = chrome_option.to_capabilities()

desired_capabilities['proxy'] = {
    "httpProxy": PROXY,
    "ftpProxy": PROXY,
    "sslProxy": PROXY,
    "noProxy": None,
    "proxyType": "MANUAL",
    "class": "org.openqa.selenium.Proxy",
    "autodetect": False
}
driver = webdriver.Chrome(desired_capabilities = desired_capabilities)

driver = WebDriver(options=chrome_option


#携带cookie
chrome_options = Options()
chrome_options.add_argument("user-data-dir=selenium") 
driver = webdriver.Chrome(chrome_options=chrome_options)
driver.get("http://www.baidu.com")


from selenium.webdriver.chrome.webdriver import Options
options= Options()

#谷歌无头模式
options.add_argument('--headless')
options.add_argument('--disable-gpu')        # 谷歌文档提到需要加上这个属性来规避bug

options.add_argument('disable-infobars')     # 隐藏"Chrome正在受到自动软件的控制"
options.add_argument('lang=zh_CN.UTF-8')     # 设置中文
options.add_argument('window-size=1920x3000')     # 指定浏览器分辨率
options.add_argument('--hide-scrollbars')         # 隐藏滚动条, 应对一些特殊页面
options.add_argument('--remote-debugging-port=9222')
options.binary_location = r'/Applications/Chrome'     #手动指定使用的浏览器位置

# 更换头部
user_agent = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " +
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"
    )

options.add_argument('user-agent=%s'%user_agent)

#设置图片不加载
prefs = {
    'profile.default_content_setting_values': {
        'images': 2
    }
}
options.add_experimental_option('prefs', prefs)
#或者  使用下面的设置, 提升速度
options.add_argument('blink-settings=imagesEnabled=false')

#设置代理
options.add_argument('proxy-server=' +'192.168.0.28:808')
driver = webdriver.Chrome(chrome_options=options)

#设置 cookie
driver.delete_all_cookies()# 删除所有的cookie
driver.add_cookie({'name':'ABC','value':'DEF'})# 携带cookie打开
driver.get_cookies()

# 通过 js 新打开一个窗口
driver.execute_script( "window.open("https://www.baidu.com");" )

# 通过 js 移动到最下
time.sleep(3)    # 等待 页面加载/Ajax数据返回
driver.execute_script( "var q=document.documentElement.scrollTop=10000" )

# 通过 js 返回所有html
driver.execute_script( "return document.documentElement.outerHTML" )


'''
class NetDriverMgr(object):
    #selenium的相关设置，必须在config文件中设置，并且在使用前（init)的时候，给与赋值
    #webDriver下载  
    #首先在chrome浏览器中，输入chrome://version 获得版本号。
    #地址 http://npm.taobao.org/mirrors/chromedriver/ 下载对应版本的文件，解压放在目录中
    #一定要事先安装了谷歌浏览器才可以。
    #一定要在目录之后加上驱动的名字，如chromedrvier
    DRIVER_PATH = "D:\Program Files\python3.9.4\chromedriver"
    DRIVER_TYPE = "Chrome"
    DEFAULT_DRIVER_TYPE = "Chrome"
    SUPPORT_DRIVER_TYPE = frozenset(["Firefox", "Chrome", "Opera", "Ie", "Edge"])
    DRIVER_INSTANCE = None
    HEADLESS = True

    #加Agent :  --user_agent = getPcUserAgent() 或者 'user_agent' = getPhoneUserAgent()
    #加Proxy :  --proxy-server = '192.168.0.28:808'
    #通过kwargs传送进来。
    @classmethod
    def create_driver(cls, **kwargs):
        try:
            from selenium import webdriver
        except ImportError:
            raise RuntimeError('pleaese install selenium first. python3 -m pip install selenium')

        if not cls.DRIVER_PATH:
            raise RuntimeError("DRIVER_PATH must be set")

        if cls.DRIVER_TYPE not in cls.SUPPORT_DRIVER_TYPE:
            raise RuntimeError(
                "DRIVER_TYPE must be: {}".format(",".join(cls.SUPPORT_DRIVER_TYPE)))

        if cls.DRIVER_INSTANCE:
            return cls.DRIVER_INSTANCE

        if cls.DRIVER_TYPE == 'Chrome' and cls.HEADLESS:
            from selenium.webdriver.chrome.options import Options
            options = Options()
            #options.add_argument('--headless') #Headless Chrome 是 Chrome 浏览器的无界面形态，可以在不打开浏览器的前提下，使用所有 Chrome 支持的特性运行你的程序。相比于现代浏览器，Headless Chrome 更加方便测试 web 应用，获得网站的截图，做爬虫抓取信息等。相比于较早的 PhantomJS，SlimerJS 等，Headless Chrome 则更加贴近浏览器环境。
            prefs = {"profile.managed_default_content_settings.images": 2}
            #options.add_experimental_option("prefs", prefs)
            options.add_experimental_option('excludeSwitches', ['enable-automation','enable-logging'])#忽略无用的错误提示
            options.add_argument('--disable-gpu')        # 谷歌文档提到需要加上这个属性来规避bug
            options.add_argument('disable-infobars')     # 隐藏"Chrome正在受到自动软件的控制"
            options.add_argument('lang=zh_CN.UTF-8')     # 设置中文

            for key,value in kwargs.items():
                print(key +" = "+value)
                options.add_argument(key +"="+value+"")

            driver = webdriver.Chrome(cls.DRIVER_PATH, options=options)
        else:
            driver = getattr(webdriver, cls.DRIVER_TYPE)(cls.DRIVER_PATH, **kwargs)
        #logger.info('new driver=%s', driver)
        cls.DRIVER_INSTANCE = driver
        return cls.DRIVER_INSTANCE

    @classmethod
    def close_driver(cls):
        if cls.DRIVER_INSTANCE:
            cls.DRIVER_INSTANCE.quit()
            cls.DRIVER_INSTANCE = None
            #logger.info('driver quit.')

    @classmethod
    def __del__(cls):
        cls.close_driver()

    @classmethod
    def set_proxy(cls,proxy):
        return

    @classmethod
    def set_userAgent(cls,agent):
        if cls.DRIVER_INSTANCE:
            cls.DRIVER_INSTANCE.execute_cdp_cmd("Emulation.setUserAgentOverride", {"userAgent": agent })
            #cls.DRIVER_INSTANCE.set_preference("general.useragent.override", agent )
            #cls.DRIVER_INSTANCE.update_preferences()
        return

    #设置 cookie
    @classmethod
    def set_cookie(cls,cookie):
        if cls.DRIVER_INSTANCE :
            cls.DRIVER_INSTANCE.delete_all_cookies()# 删除所有的cookie
            cls.DRIVER_INSTANCE.add_cookie(cookie)# 携带cookie打开

    @classmethod
    def get_cookie(cls):
        if cls.DRIVER_INSTANCE :
            cls.DRIVER_INSTANCE.get_cookies()

#测试代码
if __name__ == "__main__":
    driver = NetDriverMgr.create_driver()
    NetDriverMgr.set_userAgent(getPhoneUserAgent())
    driver.get("https://www.mkzhan.com/215599/901869.html")
    html=driver.page_source
    print(html.encode("utf8"))
    
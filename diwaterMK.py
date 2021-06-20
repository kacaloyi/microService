# -*- coding: UTF-8 -*-
'''
用python＋OpenCV去除图片水印
原理：
  把水印做成一个黑底的灰度图，黑色部分不用管，白色部分用邻近色填充。
  为了能调用cv2的填充函数，需要用程序把灰度图扩大到和要去水印的图一样大，而且要把水印模板对准图片中水印的位置。
  这个是默认水印在右下角的固定位置，（以右下角为原点）

'''
import os
import sys
import math
import time
import datetime
import cv2
import numpy as np 


fnmark = 'markMK.png'
#start_time  = "2021-06-10 14:00:00"  #修改时间早于这个时间的文件才需要处理。晚于这个时间的，应该是处理过了。

def get_formattime_from_timestamp(time_stamp):
    date_array = datetime.datetime.utcfromtimestamp(time_stamp)
    time_str = date_array.strftime("%Y-%m-%d %H:%M:%S.%f")
    return time_str

def get_timestamp_from_formattime(format_time):
    struct_time = time.strptime(format_time, '%Y-%m-%d %H:%M:%S')
    return time.mktime(struct_time)

#首先要保证fname是有效的文件名，而且文件确实存在
def get_file_time(ffullname):
    mtime = os.stat(ffullname).st_mtime
    date_array = datetime.datetime.utcfromtimestamp(mtime)
    time_str = date_array.strftime("%Y-%m-%d %H:%M:%S.%f")
    print (ffullname,time_str)
    return int(mtime)
    


def get_water(fnsource,fnmark,fnresult):

    kernel = np.ones((3,3),np.uint8)
    # 黑底白字
    src = cv2.imread(fnsource)  # 默认的彩色图(IMREAD_COLOR)方式读入原始图像
    if src is None or src.shape is None:
        return 

    h = src.shape[0]
    w = src.shape[1]

    print(fnsource,src.shape)

    # black.jpg
    mask = cv2.imread(fnmark, cv2.IMREAD_GRAYSCALE)  # 灰度图(IMREAD_GRAYSCALE)方式读入水印蒙版图像
    mh = mask.shape[0]
    mw = mask.shape[1]

    #假设水印在高度中间、水平右对齐的位置
    kl = w - mw
    kht = h-mh # math.ceil((h-mh)/2) 
    khb = 0  #math.floor((h-mh)/2) 

    #如果图片太小，小于mark的尺寸，那么是不可能有水印的，放过。
    if kl < 0 or kht <0  or khb < 0:
        return
    # 根据图像的边界的像素值，向外扩充图片，左右扩充7个像素  上下扩充14个像素。
    bmask = cv2.copyMakeBorder(mask,kht,khb,kl,0,cv2.BORDER_REPLICATE)
    print(fnmark,'扩充后',bmask.shape)
    
    #把模板膨胀一圈，盖住边缘的噪点
    dilate_mast = cv2.dilate(bmask,kernel,iterations = 1)
    # 参数：目标修复图像; 蒙版图（定位修复区域）; 选取邻域半径; 修复算法(包括INPAINT_TELEA/INPAINT_NS， 前者算法效果较好)
    '''
    dst = cv2.inpaint（src，mask, inpaintRadius，flags）
    src：输入8位1通道或3通道图像。
    inpaintMask：修复掩码，8位1通道图像。非零像素表示需要修复的区域。
    dst：输出与src具有相同大小和类型的图像。
    inpaintRadius：算法考虑的每个点的圆形邻域的半径。
    flags：
        INPAINT_NS基于Navier-Stokes的方法
        Alexandru Telea的INPAINT_TELEA方法
    '''
    try:
        #dst = cv2.inpaint(src, mask, 3, cv2.INPAINT_TELEA)
        dst = cv2.inpaint(src, dilate_mast, 3, cv2.INPAINT_TELEA)
        cv2.imwrite(fnresult, dst)
    except :
        print("处理出错：",fnsource)

def walkpath(rootdir):

    list_file = os.listdir(rootdir)
    for i in range(0,len(list_file)):
        # 构造路径
        path = os.path.join(rootdir,list_file[i])

        if os.path.isdir(path):
           print("目录",path)
           walkpath(path)
           continue
       
        if os.path.isfile(path):
        #    tt = get_timestamp_from_formattime(start_time)
        #    ft = get_file_time(path)
        #    if ft > tt :
        #        continue 
           #print (path,'\r\n')
           global fnmark
           #print (fnmark)
           get_water(path,fnmark,path)
           continue
    
     

def main(argv):

    if 3 > len( argv):
        print("用法：python diwater.py rootpath markfile")
        return

    rootpath = argv[1]
   
    global fnmark
    fnmark = argv[2]
    #print("mark:",fnmark)
    if  os.path.isfile(fnmark) == False:
        print("mark文件不存在",fnmark)
        return
    
    list_file = os.listdir(rootpath)
    # list_file = [
    #         "215451","215463","215511","215513","215518","215519","215536","215570","215580","215598","215599","215603","215608",
    #         "21562","215632","215633","215635","215640","215646","215648","215651","215670","215686","215719","215720","215725",
    #         "215737","215744","215768","215773","215778","215783","215784","215790","215795","215800","215801","215803","215808",
    #         "215823","215828","215847","215854","215880","215909","215913","215914","215915","215917","215918","215919","215921",
    #         "215927","215940","215950","215976","215980","216025","216094","26515","29","43","49733","8613"
    #         ]

    # for i in range(0,len(list_file)):
    #     ddir = os.path.join(rootpath,list_file[i])
    #     print("目录：",ddir)
    #     if  os.path.isdir(ddir):
    #         walkpath(ddir)

    walkpath(rootpath)


    return

if __name__ == "__main__":    
    main(sys.argv)
    #ft = get_file_time(sys.argv[1])
    #tt = get_timestamp_from_formattime(start_time)

    #print(tt,tt > ft)

# -*- coding: UTF-8 -*-
'''
用python＋OpenCV去除图片水印
原理：
  把水印做成一个黑底的灰度图，黑色部分不用管，白色部分用邻近色填充。
  为了能调用cv2的填充函数，需要用程序把灰度图扩大到和要去水印的图一样大，而且要把水印模板对准图片中水印的位置。
  这个是默认水印在高度中间，水平右侧的固定位置，（以水平中线与右边缘相交处为原点）

'''
import os
import sys
import math
import cv2
import numpy as np 


fnmark = 'mark.jpg'


def get_water(fnsource,fnmark,fnresult):

    kernel = np.ones((3,3),np.uint8)
    # 黑底白字
    src = cv2.imread(fnsource)  # 默认的彩色图(IMREAD_COLOR)方式读入原始图像

    h = src.shape[0]
    w = src.shape[1]

    print(fnsource,src.shape)

    # black.jpg
    mask = cv2.imread(fnmark, cv2.IMREAD_GRAYSCALE)  # 灰度图(IMREAD_GRAYSCALE)方式读入水印蒙版图像
    mh = mask.shape[0]
    mw = mask.shape[1]

    #假设水印在高度中间、水平右对齐的位置
    kl = w - mw
    kht = math.ceil((h-mh)/2) 
    khb = math.floor((h-mh)/2) 

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
    
    #dst = cv2.inpaint(src, mask, 3, cv2.INPAINT_TELEA)
    dst = cv2.inpaint(src, dilate_mast, 3, cv2.INPAINT_TELEA)
    cv2.imwrite(fnresult, dst)

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

    walkpath(rootpath)
    return

if __name__ == "__main__":    
    main(sys.argv)


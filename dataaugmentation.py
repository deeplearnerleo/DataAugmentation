# !/usr/bin/env python2
# -*- coding: utf-8 -*-


from __future__ import division

import os
import cv2
import xml.dom.minidom
from xml.dom.minidom import Document

import math




# 获取路径下所有文件的完整路径，用于读取文件用
def GetFileFromThisRootDir(dir, ext=None):
    allfiles = []
    needExtFilter = (ext != None)
    for root, dirs, files in os.walk(dir):
        for filespath in files:
            filepath = os.path.join(root, filespath)
            extension = os.path.splitext(filepath)[1][1:]
            if needExtFilter and extension in ext:
                allfiles.append(filepath)
            elif not needExtFilter:
                allfiles.append(filepath)
    return allfiles


# 图像旋转用，里面的angle是角度制的
def im_rotate(im, angle, center=None, scale=1.0):
    h, w = im.shape[:2]
    if center is None:
        center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, angle, scale)
    im_rot = cv2.warpAffine(im, M, (w, h))
    return im_rot


# 读取xml文件，xmlfile参数表示xml的路径
def readXml(xmlfile):
    DomTree = xml.dom.minidom.parse(xmlfile)
    annotation = DomTree.documentElement
    sizelist = annotation.getElementsByTagName('size')  # [<DOM Element: filename at 0x381f788>]
    heights = sizelist[0].getElementsByTagName('height')
    height = int(heights[0].childNodes[0].data)
    widths = sizelist[0].getElementsByTagName('width')
    width = int(widths[0].childNodes[0].data)
    depths = sizelist[0].getElementsByTagName('depth')
    depth = int(depths[0].childNodes[0].data)
    objectlist = annotation.getElementsByTagName('object')
    bboxes = []
    for objects in objectlist:
        namelist = objects.getElementsByTagName('name')
        class_label = namelist[0].childNodes[0].data
        bndbox = objects.getElementsByTagName('bndbox')[0]
        x1_list = bndbox.getElementsByTagName('xmin')
        x1 = int(float(x1_list[0].childNodes[0].data))
        y1_list = bndbox.getElementsByTagName('ymin')
        y1 = int(float(y1_list[0].childNodes[0].data))
        x2_list = bndbox.getElementsByTagName('xmax')
        x2 = int(float(x2_list[0].childNodes[0].data))
        y2_list = bndbox.getElementsByTagName('ymax')
        y2 = int(float(y2_list[0].childNodes[0].data))
        # 这里我box的格式【xmin，ymin，xmax，ymax，classname】
        bbox = [x1, y1, x2, y2, class_label]
        bboxes.append(bbox)
    return bboxes, width, height, depth


# 写xml文件，参数中tmp表示路径，imgname是文件名（没有尾缀）ps有尾缀也无所谓
def writeXml(tmp, imgname, w, h, d, bboxes):
    doc = Document()
    # owner
    annotation = doc.createElement('annotation')
    doc.appendChild(annotation)
    # owner
    folder = doc.createElement('folder')
    annotation.appendChild(folder)
    folder_txt = doc.createTextNode("VOC2007")
    folder.appendChild(folder_txt)

    filename = doc.createElement('filename')
    annotation.appendChild(filename)
    filename_txt = doc.createTextNode(imgname)
    filename.appendChild(filename_txt)
    # ones#
    source = doc.createElement('source')
    annotation.appendChild(source)

    database = doc.createElement('database')
    source.appendChild(database)
    database_txt = doc.createTextNode("My Database")
    database.appendChild(database_txt)

    annotation_new = doc.createElement('annotation')
    source.appendChild(annotation_new)
    annotation_new_txt = doc.createTextNode("VOC2007")
    annotation_new.appendChild(annotation_new_txt)

    image = doc.createElement('image')
    source.appendChild(image)
    image_txt = doc.createTextNode("flickr")
    image.appendChild(image_txt)
    # owner
    owner = doc.createElement('owner')
    annotation.appendChild(owner)

    flickrid = doc.createElement('flickrid')
    owner.appendChild(flickrid)
    flickrid_txt = doc.createTextNode("NULL")
    flickrid.appendChild(flickrid_txt)

    ow_name = doc.createElement('name')
    owner.appendChild(ow_name)
    ow_name_txt = doc.createTextNode("idannel")
    ow_name.appendChild(ow_name_txt)
    # onee#
    # twos#
    size = doc.createElement('size')
    annotation.appendChild(size)

    width = doc.createElement('width')
    size.appendChild(width)
    width_txt = doc.createTextNode(str(w))
    width.appendChild(width_txt)

    height = doc.createElement('height')
    size.appendChild(height)
    height_txt = doc.createTextNode(str(h))
    height.appendChild(height_txt)

    depth = doc.createElement('depth')
    size.appendChild(depth)
    depth_txt = doc.createTextNode(str(d))
    depth.appendChild(depth_txt)
    # twoe#
    segmented = doc.createElement('segmented')
    annotation.appendChild(segmented)
    segmented_txt = doc.createTextNode("0")
    segmented.appendChild(segmented_txt)

    for bbox in bboxes:
        # threes#
        object_new = doc.createElement("object")
        annotation.appendChild(object_new)

        name = doc.createElement('name')
        object_new.appendChild(name)
        name_txt = doc.createTextNode(str(bbox[4]))
        name.appendChild(name_txt)

        pose = doc.createElement('pose')
        object_new.appendChild(pose)
        pose_txt = doc.createTextNode("Unspecified")
        pose.appendChild(pose_txt)

        truncated = doc.createElement('truncated')
        object_new.appendChild(truncated)
        truncated_txt = doc.createTextNode("0")
        truncated.appendChild(truncated_txt)

        difficult = doc.createElement('difficult')
        object_new.appendChild(difficult)
        difficult_txt = doc.createTextNode("0")
        difficult.appendChild(difficult_txt)
        # threes-1#
        bndbox = doc.createElement('bndbox')
        object_new.appendChild(bndbox)

        xmin = doc.createElement('xmin')
        bndbox.appendChild(xmin)
        xmin_txt = doc.createTextNode(str(bbox[0]))
        xmin.appendChild(xmin_txt)

        ymin = doc.createElement('ymin')
        bndbox.appendChild(ymin)
        ymin_txt = doc.createTextNode(str(bbox[1]))
        ymin.appendChild(ymin_txt)

        xmax = doc.createElement('xmax')
        bndbox.appendChild(xmax)
        xmax_txt = doc.createTextNode(str(bbox[2]))
        xmax.appendChild(xmax_txt)

        ymax = doc.createElement('ymax')
        bndbox.appendChild(ymax)
        ymax_txt = doc.createTextNode(str(bbox[3]))
        ymax.appendChild(ymax_txt)

    tempfile = tmp + "%s.xml" % imgname
    with open(tempfile, 'wb') as f:
        f.write(doc.toprettyxml(indent='\t', encoding='utf-8'))
    return


# voc路径
root = '/home/ubtu/darknet/scripts/VOCdevkit/VOC2007/'
img_dir = root + 'JPEGImages/'
anno_path = root + 'Annotations/'
# 存储新的anno位置
anno_new_path = root + 'NewAnnotations/'
if not os.path.isdir(anno_new_path):
    os.makedirs(anno_new_path)
# 读取原图全路径
imgs_path = GetFileFromThisRootDir(img_dir)
# 存储旋转后图片位置
pro_dir = root + 'train_translate_scale_rotate/'
if not os.path.isdir(pro_dir):
    os.makedirs(pro_dir)
# 旋转角的大小，整数表示逆时针旋转
angles = [1, 15,30,45,60,75,90,105,120,150,180,210,240,270,359]  # 角度im_rotate用到的是角度制
angle_rad = [angle * math.pi / 180.0 for angle in angles]  # cos三角函数里要用到弧度制的
j = 0  # 计数用
angle_num = len(angles)
for img_path in imgs_path:
    # 读取原图像
    im = cv2.imread(img_path)
    #cv2.imshow(img_path)
    for i in range(angle_num):
        gt_new = []
        im_rot = im_rotate(im, angles[i])
        file_name = img_path.split('/')[-1][:-4]
        # 画出旋转后图像
        cv2.imwrite(os.path.join(pro_dir, 'P%s_%s.jpg' % (angles[i], file_name)), im_rot)
        anno = os.path.join(anno_path, '%s.xml' % file_name)
        # 读取anno标签数据
        [gts, w, h, d] = readXml(anno)
        # 计算旋转后gt框四点的坐标变换
        [xc, yc] = [float(w) / 2, float(h) / 2]
        for gt in gts:
            # 计算左上角点的变换
            x1 = (gt[0] - xc) * math.cos(angle_rad[i]) - (yc - gt[1]) * math.sin(angle_rad[i]) + xc
            if x1 < 0: x1 = 0
            if x1 > w - 1: x1 = w - 1
            y1 = yc - (gt[0] - xc) * math.sin(angle_rad[i]) - (yc - gt[1]) * math.cos(angle_rad[i])
            if y1 < 0: y1 = 0
            if y1 > h - 1: y1 = h - 1
            # 计算右上角点的变换
            x2 = (gt[2] - xc) * math.cos(angle_rad[i]) - (yc - gt[1]) * math.sin(angle_rad[i]) + xc
            if x2 < 0: x2 = 0
            if x2 > w - 1: x2 = w - 1
            y2 = yc - (gt[2] - xc) * math.sin(angle_rad[i]) - (yc - gt[1]) * math.cos(angle_rad[i])
            if y2 < 0: y2 = 0
            if y2 > h - 1: y2 = h - 1
            # 计算左下角点的变换
            x3 = (gt[0] - xc) * math.cos(angle_rad[i]) - (yc - gt[3]) * math.sin(angle_rad[i]) + xc
            if x3 < 0: x3 = 0
            if x3 > w - 1: x3 = w - 1
            y3 = yc - (gt[0] - xc) * math.sin(angle_rad[i]) - (yc - gt[3]) * math.cos(angle_rad[i])
            if y3 < 0: y3 = 0
            if y3 > h - 1: y3 = h - 1
            # 计算右下角点的变换
            x4 = (gt[2] - xc) * math.cos(angle_rad[i]) - (yc - gt[3]) * math.sin(angle_rad[i]) + xc
            if x4 < 0: x4 = 0
            if x4 > w - 1: x4 = w - 1
            y4 = yc - (gt[2] - xc) * math.sin(angle_rad[i]) - (yc - gt[3]) * math.cos(angle_rad[i])
            if y4 < 0: y4 = 0
            if y4 > h - 1: y4 = h - 1
            xmin = min(x1, x2, x3, x4)
            xmax = max(x1, x2, x3, x4)
            ymin = min(y1, y2, y3, y4)
            ymax = max(y1, y2, y3, y4)
            # 把因为旋转导致的特别小的 长线型的去掉
            w_new = xmax - xmin + 1
            h_new = ymax - ymin + 1
            ratio1 = float(w_new) / h_new
            ratio2 = float(h_new) / w_new
            if (1.0 / 6.0 < ratio1 < 6 and 1.0 / 6.0 < ratio2 < 6 and w_new > 9 and h_new > 9):
                classname = str(gt[4])
                gt_new.append([xmin, ymin, xmax, ymax, classname])
            # 写出新的xml
            writeXml(anno_new_path, 'P%s_%s' % (angles[i], file_name), w, h, d, gt_new)
    j = j + 1
    if j % 100 == 0: print
    '----%s----' % j

# !/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 11:07:38 2017
@author: cetc_ic
"""

#from __future__ import division
#import os
#import xml.dom.minidom
#import cv2

root = '/home/ubtu/darknet/scripts/VOCdevkit/VOC2007/'
# ImgPath = root+'JPEGImages'
# AnnoPath = root+'Annotations'
# ProcessedPath = root+'gt_show'

ImgPath = root + 'train_translate_scale_rotate'
AnnoPath = root + 'NewAnnotations'
ProcessedPath = root + 'gt_show_rotate'

if not os.path.exists(ProcessedPath):
    os.makedirs(ProcessedPath)

label_list = os.listdir(AnnoPath)

num = 0

for labelfile in label_list:
    xmlfile = os.path.join(AnnoPath, labelfile)
    imgfile = os.path.join(ImgPath, '%s.jpg' % labelfile[:-4])

    DomTree = xml.dom.minidom.parse(xmlfile)
    annotation = DomTree.documentElement

    #    filenamelist = annotation.getElementsByTagName('filename') #[<DOM Element: filename at 0x381f788>]
    #    filename = filenamelist[0].childNodes[0].data
    objectlist = annotation.getElementsByTagName('object')
    bboxes = []
    for objects in objectlist:
        namelist = objects.getElementsByTagName('name')
        class_label = namelist[0].childNodes[0].data

        bndbox = objects.getElementsByTagName('bndbox')[0]

        x1_list = bndbox.getElementsByTagName('xmin')
        x1 = int(float(x1_list[0].childNodes[0].data))
        y1_list = bndbox.getElementsByTagName('ymin')
        y1 = int(float(y1_list[0].childNodes[0].data))
        x2_list = bndbox.getElementsByTagName('xmax')
        x2 = int(float(x2_list[0].childNodes[0].data))
        y2_list = bndbox.getElementsByTagName('ymax')
        y2 = int(float(y2_list[0].childNodes[0].data))

        bbox = [x1, y1, x2, y2, class_label]
        bboxes.append(bbox)

    img = cv2.imread(imgfile)
    for bbox in bboxes:
        x1 = bbox[0]
        y1 = bbox[1]
        x2 = bbox[2]
        y2 = bbox[3]

        if x1 < 0: x1 = 0
        if y1 < 0: y1 = 0
        if x2 > img.shape[1] - 1: x2 = img.shape[1] - 1
        if y2 > img.shape[0] - 1: y2 = img.shape[0] - 1

        cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 0), 2)
        # cv2.putText(img,bbox[4],(bbox[0],bbox[1]),0.6,cv2.FONT_HERSHEY_SIMPLEX,2)
    cv2.imwrite(os.path.join(ProcessedPath, '%s.jpg' % labelfile[:-4]), img)
    print
    labelfile

    num += 1
    print
    num

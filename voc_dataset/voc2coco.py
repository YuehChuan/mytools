#!/usr/bin/python

# pip install lxml

import sys
import os
import json
import xml.etree.ElementTree as ET
from shutil import copyfile

START_BOUNDING_BOX_ID = 1
PRE_DEFINE_CATEGORIES = {}
# If necessary, pre-define category and its id
#  PRE_DEFINE_CATEGORIES = {"aeroplane": 1, "bicycle": 2, "bird": 3, "boat": 4,
                         #  "bottle":5, "bus": 6, "car": 7, "cat": 8, "chair": 9,
                         #  "cow": 10, "diningtable": 11, "dog": 12, "horse": 13,
                         #  "motorbike": 14, "person": 15, "pottedplant": 16,
                         #  "sheep": 17, "sofa": 18, "train": 19, "tvmonitor": 20}


def get(root, name):
    vars = root.findall(name)
    return vars


def get_and_check(root, name, length):
    vars = root.findall(name)
    if len(vars) == 0:
        raise NotImplementedError('Can not find %s in %s.'%(name, root.tag))
    if length > 0 and len(vars) != length:
        raise NotImplementedError('The size of %s is supposed to be %d, but is %d.'%(name, length, len(vars)))
    if length == 1:
        vars = vars[0]
    return vars


def get_filename_as_int(filename):
    try:
        filename = os.path.splitext(filename)[0]
        return int(filename)
    except:
        raise NotImplementedError('Filename %s is supposed to be an integer.'%(filename))


def convert(xml_list, xml_dir, json_file):
    list_fp = open(xml_list, 'r')
    json_dict = {"images":[], "type": "instances", "annotations": [],
                 "categories": []}
    categories = PRE_DEFINE_CATEGORIES
    bnd_id = START_BOUNDING_BOX_ID
    for line in list_fp:
        line = line.strip()
        base_name = line
        line += '.xml'
        print("Processing %s"%(line))
        xml_f = os.path.join(xml_dir, line)
        tree = ET.parse(xml_f)
        root = tree.getroot()
        path = get(root, 'path')
        #if len(path) == 1:
        #    filename = os.path.basename(path[0].text)
        #elif len(path) == 0:
        #filename = get_and_check(root, 'filename', 1).text
        filename = base_name + img_ext
        #else:
        #    raise NotImplementedError('%d paths found in %s'%(len(path), line))
        ## The filename must be a number
        print("TEST:", filename)
        image_id = get_filename_as_int(filename)
        size = get_and_check(root, 'size', 1)
        width = int(get_and_check(size, 'width', 1).text)
        height = int(get_and_check(size, 'height', 1).text)
        image = {'file_name': filename, 'height': height, 'width': width,
                 'id':image_id}
        json_dict['images'].append(image)
        ## Cruuently we do not support segmentation
        #  segmented = get_and_check(root, 'segmented', 1).text
        #  assert segmented == '0'
        for obj in get(root, 'object'):
            category = get_and_check(obj, 'name', 1).text
            if category not in categories:
                new_id = len(categories)
                categories[category] = new_id
            category_id = categories[category]
            bndbox = get_and_check(obj, 'bndbox', 1)
            xmin = int(get_and_check(bndbox, 'xmin', 1).text) - 1
            ymin = int(get_and_check(bndbox, 'ymin', 1).text) - 1
            xmax = int(get_and_check(bndbox, 'xmax', 1).text)
            ymax = int(get_and_check(bndbox, 'ymax', 1).text)
            assert(xmax > xmin)
            assert(ymax > ymin)
            o_width = abs(xmax - xmin)
            o_height = abs(ymax - ymin)
            ann = {'area': o_width*o_height, 'iscrowd': 0, 'image_id':
                   image_id, 'bbox':[xmin, ymin, o_width, o_height],
                   'category_id': category_id, 'id': bnd_id, 'ignore': 0,
                   'segmentation': []}
            json_dict['annotations'].append(ann)
            bnd_id = bnd_id + 1

    for cate, cid in categories.items():
        cat = {'supercategory': 'none', 'id': cid, 'name': cate}
        json_dict['categories'].append(cat)
    json_fp = open(json_file, 'w')
    json_str = json.dumps(json_dict)
    json_fp.write(json_str)
    json_fp.close()
    list_fp.close()


if __name__ == '__main__':
    #if len(sys.argv) <= 1:
    #    print('3 auguments are need.')
    #    print('Usage: %s XML_LIST.txt XML_DIR OUTPU_JSON.json'%(sys.argv[0]))
    #    exit(1)

    img_ext = '.jpg'
    IMG_FOLDER = "/DATA1/Datasets_mine/labeled/12_hand_gestures_VOC/JPEGImages"
    XML_FOLDER = "/DATA1/Datasets_mine/labeled/12_hand_gestures_VOC/ImageSets/Main/"
    XML_LIST = ["train.txt", "val.txt"]
    XML_DIR = "/DATA1/Datasets_mine/labeled/12_hand_gestures_VOC/Annotations"
    #COCO
    OUTPUT_COCO = "/DATA1/Datasets_mine/labeled/12_hand_gestures_COCO"

    if not os.path.exists(OUTPUT_COCO):
        os.makedirs(OUTPUT_COCO)

    coco_annot_path = os.path.join(OUTPUT_COCO, "annotations")
    if not os.path.exists(coco_annot_path):
        os.makedirs(coco_annot_path)

    coco_train_path = os.path.join(OUTPUT_COCO, "train2017")
    if not os.path.exists(coco_train_path):
        os.makedirs(coco_train_path)

    coco_val_path = os.path.join(OUTPUT_COCO, "val2017")
    if not os.path.exists(coco_val_path):
        os.makedirs(coco_val_path)

    f = open( os.path.join(XML_FOLDER, XML_LIST[0])  )
    line = f.readline()
    while line:
        line = f.readline()
        line = line.strip()
        if(len(line)>0):
            img_path = os.path.join( IMG_FOLDER, line+img_ext)
            copyfile(img_path, os.path.join(OUTPUT_COCO, "train2017", line+img_ext))

    f.close()

    f = open( os.path.join(XML_FOLDER, XML_LIST[1])  )
    line = f.readline()
    while line:
        line = f.readline()
        line = line.strip()
        if(len(line)>0):
            img_path = os.path.join( IMG_FOLDER, line+img_ext)
            copyfile(img_path, os.path.join(OUTPUT_COCO, "val2017", line+img_ext))

    f.close()

    for xml_file in XML_LIST:
        XML_FILE_PATH = os.path.join(XML_FOLDER, xml_file)
        if(xml_file == "train.txt"):
            COCO_ANNOT_PATH = os.path.join(coco_annot_path, "instances_train2017.json")
        else:
            COCO_ANNOT_PATH = os.path.join(coco_annot_path, "instances_val2017.json")

        print(XML_FILE_PATH, XML_DIR, COCO_ANNOT_PATH)
        convert(XML_FILE_PATH, XML_DIR, COCO_ANNOT_PATH)
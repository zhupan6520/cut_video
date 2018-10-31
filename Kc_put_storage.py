# encoding=utf8
# import sys
import os
import json
import bson.binary
import datetime
import io
import uuid

from pymongo import MongoClient

# reload(sys)
# sys.setdefaultencoding('utf8')

data = json.load(io.open('./cfg/config.json', "r", encoding='utf-8'))
mongodb_config = data['mongodb_config']
task_type = data['put_storage']['task_type']


class MongodbConnect(object):
    def con(self):
        client = MongoClient(mongodb_config['host'], mongodb_config['port'])
        db = client[mongodb_config['database']]
        return db


mongodb_connect = MongodbConnect()


def insert_data(dir_name, path):
    db = mongodb_connect.con()
    coll1 = db[mongodb_config['col_label_packet']]
    coll2 = db[mongodb_config['col_label_task']]
    coll3 = db[mongodb_config['col_label_img']]
    coll4 = db[mongodb_config['label_task_category']]
    identification = dir_name + '_' + datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    dir_path = os.path.join(path, dir_name)
    v_num = datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '_' + 'v1'
    task_type_id = coll4.find({'category_name': task_type})[0]['_id']
    coll1.save(dict(
        _id=identification,
        folder=dir_name,
        task_type=task_type_id,
        v_num=[v_num],
        user='',
        team='',
        state='0',
        check_state='0',
        create_time=datetime.datetime.utcnow() + datetime.timedelta(hours=8),
        start_T_time=datetime.datetime.utcnow() + datetime.timedelta(hours=8),
        end_T_time=datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    ))
    for root, dir_names, file_names in os.walk(dir_path):
        for filename in file_names:
            task_dic = {}
            img_dic = {}
            if filename.endswith(('.json',)):
                file_path = os.path.join(root, filename)
                with open(file_path, 'r') as load_f:
                    load_dict = json.load(load_f)
                img_id = str(uuid.uuid1())
                img_dic['_id'] = img_id
                img_dic['packet_id'] = identification
                img_dic['img_name'] = load_dict['filename']
                with open(os.path.join(root, load_dict['filename']), 'rb') as myimage:
                    img_dic['img_source'] = bson.binary.Binary(myimage.read())
                coll3.save(img_dic)

                task_dic['_id'] = str(uuid.uuid1())
                task_dic['packet_id'] = identification
                task_dic['pic_id'] = img_id
                task_dic['v_num'] = v_num
                task_dic['json_data'] = load_dict
                coll2.save(task_dic)
    print(dir_name, 'Completion of the import !!!')

# encoding=utf8
import io
import sys
import os
import re
import json
import time
import shutil

from multiprocessing import Pool
from multiprocessing import cpu_count

from Kc_put_storage import insert_data
from Kc_read_video import read_video

reload(sys)
sys.setdefaultencoding('utf8')

load_dict = json.load(io.open('./cfg/config.json', "r", encoding='utf-8'))
video_path_one = load_dict["dependencies"]["input_path"]
frame_num = load_dict["dependencies"]["frame_num"]
temporary_path = load_dict["dependencies"]["temporary_path"]
stop_img_num = load_dict["dependencies"]["stop_img_num"]
img_bao_num = load_dict["dependencies"]["img_bao_num"]


def run_Kc_mi():
    while True:
        video_path_1 = os.listdir(video_path_one)
        jc_num = Pool(cpu_count())
        for i in video_path_1:
            video_file_path = "%s/%s" % (video_path_one.decode('utf-8'), i)
            video_name = '_'.join(re.compile(r"[A-Za-z0-9]+").findall(str(i))).replace("_ts", ".ts")
            new_path = os.path.join(video_path_one, video_name)
            print(video_file_path, new_path)
            os.rename(video_file_path, new_path)
            try:
                jc_num.apply_async(read_video, (new_path, video_name.split(".")[0], frame_num,))
                print(new_path, video_name, frame_num, )
            except Exception as e:
                print(e, "the video_path is Error, Waiting for incoming video!!!")
                continue
        jc_num.close()
        jc_num.join()
        print("the video_path is None, Waiting for incoming video!!!")
        list_img_dir = os.listdir(temporary_path)
        for i_dir in list_img_dir:
            img_dir = os.path.join(temporary_path, i_dir)
            list_img = os.listdir(img_dir)
            if len(list_img) >= 2:
                insert_data(i_dir, temporary_path)
                shutil.rmtree(img_dir)
            else:
                shutil.rmtree(img_dir)
        time.sleep(30)


if __name__ == '__main__':
    run_Kc_mi()

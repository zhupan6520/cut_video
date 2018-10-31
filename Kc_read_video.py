# encoding=utf8
import io
# import sys
import os
import cv2
import json
import dlib

from PIL import Image

from Kc_put_storage import insert_data

# reload(sys)
# sys.setdefaultencoding('utf8')

load_dict = json.load(io.open('./cfg/config.json', "r", encoding='utf-8'))
video_path_one = load_dict["dependencies"]["input_path"]
frame_num = load_dict["dependencies"]["frame_num"]
temporary_path = load_dict["dependencies"]["temporary_path"]
stop_img_num = load_dict["dependencies"]["stop_img_num"]
img_bao_num = load_dict["dependencies"]["img_bao_num"]
print(frame_num, video_path_one, temporary_path, stop_img_num)


def read_video(video_file_path, video_name, frame_num):
    img_num = 1
    try:
        cap = cv2.VideoCapture(video_file_path)
        print(cap.isOpened())
    except:
        print("Invalid file %s" % video_file_path)
        # os.remove(video_file_path)
        return
    frame_count = 0
    success = True
    while (success):
        success, frame = cap.read()
        get_frame = frame_count % frame_num
        bao_num = img_num // img_bao_num + 1
        if frame_count == stop_img_num:
            break
        if get_frame == 0:
            params = []
            params.append(1)
            f_path = "%s_%s" % (video_name, bao_num)
            Timg_path = os.path.join(temporary_path, f_path)
            if not os.path.exists(Timg_path):
                os.makedirs(Timg_path)
            img_name = "%s_%04d.jpg" % (video_name, img_num)
            img_path = "%s/%s" % (Timg_path, img_name)
            cv2.imwrite(img_path, frame, params)
            print("get img %s" % img_path)
            img_num = detection_result(img_path, f_path, img_name, img_num)
        frame_count = frame_count + 1
    cap.release()
    os.remove(video_file_path)


def detection_result(img_path, f_path, img_name, img_num):
    detector = dlib.get_frontal_face_detector()
    index = 1
    box_list = []
    try:
        img = cv2.imread(img_path)
        img1 = Image.open(img_path)
        img_m = list(img1.size)
        if len(img.shape) == 3 or len(img.shape) == 4:
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray_img = img
        det_s = detector(gray_img, 1)
    except Ellipsis as e:
        print("Error reading picture !!!", img_path, e)
        os.remove(img_path)
        return img_num
    for i, d in enumerate(det_s):
        x1 = int(d.left()) if d.left() > 0 else 0
        y1 = int(d.top()) if d.top() > 0 else 0
        x2 = int(d.right()) if d.right() > 0 else 0
        y2 = int(d.bottom()) if d.bottom() > 0 else 0
        x_1 = int((x1 + x2) * 0.5 - ((x2 - x1) * 0.5 * 1.2))
        y_1 = int((y1 + y2) * 0.5 - ((y2 - y1) * 0.5 * 1.8))
        x_2 = int((x1 + x2) * 0.5 + ((x2 - x1) * 0.5 * 1.2))
        y_2 = int((y1 + y2) * 0.5 + ((y2 - y1) * 0.5 * 1.1))
        box = (index, x_1, y_1, x_2, y_2)
        box_list.append(box)
        index += 1
    list_box = []
    if len(box_list) == 0:
        print("No items found !!!", img_path)
        os.remove(img_path)
        return img_num
    else:
        for i in box_list:
            m = {"bndbox": {"xmin": "%s" % str(i[1]), "ymin": "%s" % str(i[2]), "ymax": "%s" % str(i[4]),
                            "xmax": "%s" % str(i[3])}, "difficult": "0", "pose": "Unspecified",
                 "name": "%s" % str(i[0]), "truncated": "0"}
            list_box.append(m)
    with open(str(img_path).replace(".jpg", ".json"), "w") as f:
        # print(str(img_path).replace(".jpg", ".json"))
        img_json = {"source": {"database": "Unknown"}, "filename": "%s" % img_name, "segmented": "0",
                    "objects": list_box, "path": "%s" % img_path, "folder": "%s" % f_path,
                    "size": {"width": "%s" % img_m[0], "depth": "3", "height": "%s" % img_m[1]}}
        json.dump(img_json, f, ensure_ascii=False)
    print(img_json)
    img_num += 1
    return img_num

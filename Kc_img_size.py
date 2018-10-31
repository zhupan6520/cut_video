from PIL import Image
import os


def img_size(img_path):
    img = Image.open(img_path)
    print(img.size)
    new_path = img_path.replace(".jpg", ".png")
    img.resize((int(img.size[0] * 0.5), int(img.size[1] * 0.5))).save(new_path, "JPEG")
    print(new_path)


if __name__ == '__main__':
    small_path = r"D:\test\img"
    list_img = os.listdir(small_path)
    for img in list_img:
        if img.endswith(".jpg"):
            img_path = os.path.join(small_path, img)
            img_size(img_path)
        else:
            continue

import json
import os
import requests
import shutil
from natsort import natsorted
from urllib.parse import unquote
from urllib.parse import quote
import numpy as np

baseURL = 'https://molar-app-prod-v5.oss-cn-hangzhou.aliyuncs.com/'
def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as fp:
        s = fp.read()
        data = json.loads(s)
    return data

def load_jsonl(url):
    data = []
    with open(url, 'r', encoding='utf-8') as f:
        for i in f:
            json_data = json.loads(i)
            data.append(json_data)
    return data

def write_json(data, file_path):
    output = json.dumps(data, indent=4, ensure_ascii=False)
    with open(file_path, "w+", encoding="utf-8") as file:
        file.write(output)
    return True

def create_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    else:
        return False
    
def get_file_names(directory):
    file_names = natsorted(os.listdir(directory))
    return file_names

def get_folder_names(directory):
    folder_names = natsorted(next(os.walk(directory))[1], key=str.lower)
    return folder_names

def rename_folder(old_name, new_name):
    os.rename(old_name, new_name)

def download_image(url, save_path):
    try:
        # 发送 GET 请求
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        # 以二进制写入模式保存图片
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(1024):  # 分块写入，避免内存占用过大
                file.write(chunk)
        print(f"图片已保存至: {save_path}")
    except Exception as e:
        print(f"下载失败: {e}")

from PIL import Image

def crop_image(input_path, output_path, left, top, right, bottom):
    """
    裁剪图片并保存
    :param input_path: 输入图片路径
    :param output_path: 输出图片路径
    :param left: 左上角 x 坐标
    :param top: 左上角 y 坐标
    :param right: 右下角 x 坐标
    :param bottom: 右下角 y 坐标
    """
    with Image.open(input_path) as img:
        # 裁剪图片 (left, top, right, bottom)
        cropped_img = img.crop((left, top, right, bottom))
        cropped_img.save(output_path)
        print(f"图片已裁剪并保存至: {output_path}")

def move_file(source_path, destination_path):
    try:
        shutil.move(source_path, destination_path)
    except Exception as e:
        print(f"移动失败: {e}")

def copy_any(source_path, destination_path):
    try:
        if os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)
        elif os.path.isfile(source_path):
            shutil.copy(source_path, destination_path)
        else:
            print("源路径无效：既不是文件也不是文件夹")
    except Exception as e:
        print(f"复制失败: {e}")

def rename_file(old_path, new_path):
    try:
        os.rename(old_path, new_path)
    except Exception as e:
        print(f"重命名失败: {e}")

def delete_file(file_path):
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"删除失败: {e}")

def unqt(str):
    return unquote(str)

def qt(str):
    return quote(str)

def camera_inverse_files(input_path, output_path):
    with open(input_path,'r',encoding='utf8')as fp:
        s = fp.read()
        data = json.loads(s)

    total = 0
    for i in data:
        A = np.array(i["extrinsic"])
        A_inv = np.linalg.inv(A)
        output = []
        t = 0
        for j in A_inv:
            output.append([])
            for k in j:
                output[t].append(float(k))
            t += 1
        
        data[total]['extrinsic'] = output
        total += 1

    json_str = json.dumps(data, indent=4, ensure_ascii=False)
    with open(output_path, "w+", encoding="utf-8") as file:
        file.write(json_str)

def camera_inverse_str(input_str):
    data = input_str

    total = 0
    for i in data:
        A = np.array(i["extrinsic"])
        A_inv = np.linalg.inv(A)
        output = []
        t = 0
        for j in A_inv:
            output.append([])
            for k in j:
                output[t].append(float(k))
            t += 1
        
        data[total]['extrinsic'] = output
        total += 1

    return data
                

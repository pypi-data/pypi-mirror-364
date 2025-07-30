import os
import shutil
from natsort import natsorted
from urllib.parse import unquote
from urllib.parse import quote

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
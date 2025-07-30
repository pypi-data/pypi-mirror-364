import subprocess
from tqdm import tqdm
import multiprocessing
from pathlib import Path

def process(row, potree_converter_executable, output_folder_name):
    save_path = row.parent / output_folder_name

    save_path.mkdir(parents=True, exist_ok=True)
    command = [
        potree_converter_executable,
        row,
        "-o", save_path
        
    ]
    log = subprocess.run(command, capture_output=True)
    if log.returncode != 0:
        error_message = f"Error processing {row}: {log.stderr.decode()}\n"
        with open("conversion_errors.txt", "a") as error_file:
            error_file.write(error_message)

def las_2_octree(data_path, item_clip_name = "",
                potree_converter_url = r"D:\PotreeConverter_windows_x64\PotreeConverter.exe",
                output_folder_name = "combineLidar"):
    lasPath = []
    for item_clip in tqdm(Path(data_path).iterdir()):     # 每份las在clip目录下
        if item_clip_name == "" or item_clip.name == item_clip_name:
            lasPath.append(item_clip)

    print(f'待处理：{len(lasPath)}')

    with multiprocessing.Pool(15) as pool:
        for _ in tqdm(pool.imap_unordered(process, lasPath, potree_converter_url, output_folder_name), total=len(lasPath)):
            pass

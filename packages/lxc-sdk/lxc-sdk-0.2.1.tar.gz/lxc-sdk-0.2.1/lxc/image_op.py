import requests
from PIL import Image

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
import time
import cv2
import os
import base64
from utill_cos import *
import pyrealsense2 as rs
import numpy as np


# 定义获取图像并上传到COS的函数
def get_image_and_upload_to_cos():
    # 创建一个 CameraCapture 类的实例
    camera_capture = CameraCapture(cap_num=0)

    # 使用 open_camera 方法获取摄像头
    cap = camera_capture.open_camera()
    if cap is None:
        return None

    # 增加延迟，等待摄像头初始化
    time.sleep(2)

    # 读取一帧
    success, frame = cap.read()
    if not success:
        print("无法获取图像")
        cap.release()
        return None

    # 将图像编码为JPEG格式的二进制数据
    _, buffer = cv2.imencode('.jpg', frame)
    image_data = buffer.tobytes()  # 转换为字节数据

    # 释放摄像头
    cap.release()

    # 上传图片到腾讯云 COS
    object_key = f'rgb_image_{int(time.time())}.jpg'  # 使用时间戳生成唯一文件名
    image_url = upload_image(image_data, object_key)  # 调用上传函数
    
    # if image_url:
    #     print("图片的访问URL为:", image_url)
    # else:
    #     print("上传失败")
    return image_url


# def get_image_url_now():
#     """
#     截图并保存到 now_images 文件夹，返回可访问的图片 URL。
#     """
#     # 创建一个 CameraCapture 类的实例
#     camera_capture = CameraCapture(cap_num=0)

#     # 使用 open_camera 方法获取摄像头
#     cap = camera_capture.open_camera()
#     if cap is None:
#         return None

#     # 增加延迟，等待摄像头初始化
#     time.sleep(2)

#     # 读取一帧
#     success, frame = cap.read()
#     if not success:
#         print("无法获取图像")
#         cap.release()
#         return None

#     # 获取当前脚本所在目录并确保 now_images 文件夹存在
#     current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本的绝对路径
#     now_images_dir = os.path.join(current_dir, 'now_images')
#     if not os.path.exists(now_images_dir):
#         os.makedirs(now_images_dir)
#         print(f"已创建目录: {now_images_dir}")

#     # 构建保存的图像路径
#     image_name = 'current_image.jpg'  # 文件名可以动态生成，如加上时间戳
#     image_path = os.path.join(now_images_dir, image_name)

#     # 尝试保存图像到文件
#     if cv2.imwrite(image_path, frame):
#         print(f"图像已成功保存到 {image_path}")
#     else:
#         print(f"保存图像到 {image_path} 失败")
#         cap.release()
#         return None

#     # 释放摄像头
#     cap.release()

#     # 构建并返回本地服务器的 URL
#     image_url = f"http://localhost:8888/{image_name}"
#     return image_url

# # 定义获取图像base64的函数
# def get_image_base64_now():
#     # 创建一个 CameraCapture 类的实例
#     camera_capture = CameraCapture(cap_num=0)

#     # 使用 open_camera 方法获取摄像头
#     cap = camera_capture.open_camera()
#     if cap is None:
#         return None
    
#     # 增加延迟，等待摄像头初始化
#     time.sleep(2)

#     # 读取一帧
#     success, frame = cap.read()
#     if not success:
#         print("无法获取图像")
#         cap.release()
#         return None

#     # 获取当前脚本所在目录并确保 now_images 文件夹存在
#     current_dir = os.path.dirname(os.path.abspath(__file__))  # 获取当前脚本的绝对路径
#     now_images_dir = os.path.join(current_dir, 'now_images')
#     if not os.path.exists(now_images_dir):
#         os.makedirs(now_images_dir)
#         print(f"已创建目录: {now_images_dir}")

#     # 构建保存的图像路径
#     image_path = os.path.join(now_images_dir, 'current_image.jpg')

#     # 尝试保存图像到文件
#     if cv2.imwrite(image_path, frame):
#         print(f"图像已成功保存到 {image_path}")
#     else:
#         print(f"保存图像到 {image_path} 失败")
#         cap.release()
#         return None

#     # 将图像编码为Base64
#     _, buffer = cv2.imencode('.jpg', frame)
#     image_base64 = base64.b64encode(buffer).decode('utf-8')

#     # 释放摄像头
#     cap.release()

#      # # 将Base64编码转换为可用的图像URL
#     # image_url = 'data:image/jpeg;base64,' + image_base64

#     return image_base64

# 定义保存图片函数
def save_image(image, addr, num):
    # 保存图像文件
    image_path = f"{addr}{num}.jpg"
    cv2.imwrite(image_path, image)
    print(f"保存图像: {image_path}")

    # 将图像编码为Base64
    _, buffer = cv2.imencode('.jpg', image)
    image_base64 = base64.b64encode(buffer).decode('utf-8')

    # 保存Base64编码到文件
    base64_path = f"{addr}{num}.txt"
    with open(base64_path, 'w') as f:
        f.write(image_base64)
        print(f"保存Base64编码: {base64_path}")

class CameraCapture:
    def __init__(self, cap_num=0):
        # 初始化摄像头编号
        self.cap_num = cap_num
        self.i = 0  # 计数器
        self.timeF = 50  # 每50帧保存一张图
        self.j = 0  # 保存的图像编号

        # 获取当前工作目录并构建输出目录的绝对路径
        current_directory = os.getcwd()
        self.output_dir = os.path.join(current_directory, 'output', 'image')  

        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)

    def open_camera(self):
        # 开启摄像头
        cap = cv2.VideoCapture(self.cap_num)

        if not cap.isOpened():
            print(f"无法打开摄像头 {self.cap_num}")
            return None

        print(f"摄像头 {self.cap_num} 开启成功！")
        return cap

    def start_capture(self):
        cap = self.open_camera()
        if cap is None:
            return

        while True:
            success, frame = cap.read()
            if not success:
                print("读取帧失败，退出...")
                break

            self.i += 1
            if self.i % self.timeF == 0:
                self.j += 1
                save_image(frame, self.output_dir + '/', self.j)

            # 显示当前帧
            cv2.imshow('Camera Feed', frame)

            # 按 'q' 键退出
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # 释放摄像头和窗口
        cap.release()
        cv2.destroyAllWindows()


class CameraCapture:

    def __init__(self, cap_num=0):
    # 初始化摄像头编号
        self.cap_num = cap_num
        self.i = 0  # 计数器
        self.timeF = 50  # 每50帧保存一张图
        self.j = 0  # 保存的图像编号


    def open_camera(self):
    # 开启摄像头
        cap = cv2.VideoCapture(self.cap_num)

        if not cap.isOpened():
            print(f"无法打开摄像头 {self.cap_num}")
            return None

        print(f"摄像头 {self.cap_num} 开启成功！")
        return cap
    

    def start_capture(self):
        cap = self.open_camera()
        if cap is None:
            return

        while True:
            success, frame = cap.read()
            if not success:
                print("读取帧失败，退出...")
                break

                # 将当前帧编码为Base64格式
            _, buffer = cv2.imencode('.jpg', frame)  # 使用JPEG格式编码
            image_base64 = base64.b64encode(buffer).decode('utf-8')  # 编码为Base64并解码为字符串

    # 释放摄像头和窗口
        cap.release()
        cv2.destroyAllWindows()
        return image_base64

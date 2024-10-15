from pyorbbecsdk import Pipeline, Config, OBSensorType, OBFormat
import cv2
import numpy as np
import time
import os
from utill_cos import upload_image  # 导入 upload_image 函数

ESC_KEY = 27
PRINT_INTERVAL = 1  # 打印间隔，单位为秒
MIN_DEPTH = 20  # 最小深度，单位为毫米
MAX_DEPTH = 10000  # 最大深度，单位为毫米

# 创建输出目录
output_dir = os.path.join(os.path.dirname(__file__), 'output')
os.makedirs(output_dir, exist_ok=True)

class TemporalFilter:
    def __init__(self, alpha):
        self.alpha = alpha  # 滤波系数
        self.previous_frame = None  # 上一帧

    def process(self, frame):
        # 处理当前帧，与上一帧进行加权融合
        if self.previous_frame is None:
            result = frame  # 如果没有上一帧，返回当前帧
        else:
            result = cv2.addWeighted(frame, self.alpha, self.previous_frame, 1 - self.alpha, 0)
        self.previous_frame = result  # 更新上一帧
        return result

def get_depth_image_url():
    config = Config()  # 配置对象
    pipeline = Pipeline()  # 创建管道对象
    temporal_filter = TemporalFilter(alpha=0.5)  # 创建时间滤波器实例，alpha=0.5
    
    profile_list = pipeline.get_stream_profile_list(OBSensorType.DEPTH_SENSOR)
    if profile_list is None:
        return None
    
    depth_profile = profile_list.get_default_video_stream_profile()
    if depth_profile is None:
        return None
    
    config.enable_stream(depth_profile)
    pipeline.start(config)
    image_url = None
    
    while True:
        try:
            frames = pipeline.wait_for_frames(100)
            if frames is None:
                continue
            depth_frame = frames.get_depth_frame()
            if depth_frame is None:
                continue
            
            width = depth_frame.get_width()
            height = depth_frame.get_height()
            scale = depth_frame.get_depth_scale()

            depth_data = np.frombuffer(depth_frame.get_data(), dtype=np.uint16)
            depth_data = depth_data.reshape((height, width))

            depth_data = depth_data.astype(np.float32) * scale
            depth_data = np.where((depth_data > MIN_DEPTH) & (depth_data < MAX_DEPTH), depth_data, 0)
            depth_data = depth_data.astype(np.uint16)

            depth_data = temporal_filter.process(depth_data)

            depth_image = cv2.normalize(depth_data, None, 0, 255, cv2.NORM_MINMAX, dtype=cv2.CV_8U)
            depth_colored_image = cv2.applyColorMap(depth_image, cv2.COLORMAP_JET)

            depth_image_filename = os.path.join(output_dir, 'depth_image.jpg')
            cv2.imwrite(depth_image_filename, depth_colored_image)

            with open(depth_image_filename, 'rb') as f:
                image_data = f.read()
                object_key = f'depth_image_{int(time.time())}.jpg'
                image_url = upload_image(image_data, object_key)
            
            if image_url:
                print("图片的访问URL为:", image_url)
            else:
                print("上传失败")
            
            break
            
        except KeyboardInterrupt:
            break
            
    pipeline.stop()
    return image_url

if __name__ == "__main__":
    image_url = get_depth_image_url()
    if image_url:
        print(image_url)  # 仅打印最终的URL

import os
import subprocess
# from get_depth_image import *

# 文件路径常量
INSTALL_LIB_PATH = "/home/agilex/MLLM/MLLM_Limo_Car/pyorbbecsdk-main/install/lib"
UDEV_SCRIPT_PATH = "/home/agilex/MLLM/MLLM_Limo_Car/pyorbbecsdk-main/scripts/install_udev_rules.sh"
EXAMPLE_SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'get_depth_image.py')

def setup_paths():
    """设置 PYTHONPATH 和 LD_LIBRARY_PATH."""
    current_pythonpath = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = f"{current_pythonpath}:{INSTALL_LIB_PATH}" if current_pythonpath else INSTALL_LIB_PATH
    
    current_ld_library_path = os.environ.get("LD_LIBRARY_PATH", "")
    os.environ["LD_LIBRARY_PATH"] = f"{current_ld_library_path}:{INSTALL_LIB_PATH}" if current_ld_library_path else INSTALL_LIB_PATH

def install_udev_rules():
    """安装 udev 规则."""
    try:
        # 运行 udev 安装脚本，重定向输出
        subprocess.run(['sudo', 'bash', UDEV_SCRIPT_PATH], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # 重新加载 udev 规则
        subprocess.run(['sudo', 'udevadm', 'control', '--reload-rules'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['sudo', 'udevadm', 'trigger'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        pass  # 忽略错误

import subprocess

def run_function():
    """运行 get_deep_rgb_images.py 示例并返回图像URL."""
    try:
        result = subprocess.run(
            ['python3', EXAMPLE_SCRIPT_PATH],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        output = result.stdout.decode('utf-8').strip()

        # 查找输出中包含 "图片的访问URL为:" 的行，并提取 URL
        for line in output.splitlines():
            if "图片的访问URL为:" in line:
                # 提取并返回 URL 部分
                url = line.split("图片的访问URL为:")[-1].strip()
                return url
        
        return None  # 如果没有找到URL，返回None

    except subprocess.CalledProcessError as e:
        print(f"运行失败: {e}")
        return None

def load_depth_camera():
    """加载深度相机环境."""
    setup_paths()  # 设置环境变量
    install_udev_rules()  # 安装 udev 规则
    print("深度相机环境加载成功")
    
    image_depth_url = run_function()  # 获取图像的URL
    if image_depth_url:
        # print("深度图像获取成功:", image_depth_url)
        # print("-----------------------")
        # print("url:", image_depth_url)
        return image_depth_url  # 返回获取的图像URL
    else:
        print("深度图像获取失败")
        return None

if __name__ == '__main__':
    load_depth_camera()  # 执行加载深度相机环境的操作


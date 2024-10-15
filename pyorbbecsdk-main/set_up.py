import os
import subprocess
# from get_deep_rgb_images import *

def setup_paths():
    # 设置 PYTHONPATH 和 LD_LIBRARY_PATH
    install_lib_path = "/home/agilex/MLLM/MLLM_Limo_Car/pyorbbecsdk-main/install/lib"  # 使用绝对路径

    # 设置 PYTHONPATH
    if "PYTHONPATH" in os.environ:
        os.environ["PYTHONPATH"] += f":{install_lib_path}"  # 添加到现有 PYTHONPATH
    else:
        os.environ["PYTHONPATH"] = install_lib_path  # 初始化 PYTHONPATH
    print("PYTHONPATH set to:", os.environ["PYTHONPATH"])

    # 设置 LD_LIBRARY_PATH
    if "LD_LIBRARY_PATH" in os.environ:
        os.environ["LD_LIBRARY_PATH"] += f":{install_lib_path}"  # 添加到现有 LD_LIBRARY_PATH
    else:
        os.environ["LD_LIBRARY_PATH"] = install_lib_path  # 初始化 LD_LIBRARY_PATH
    print("LD_LIBRARY_PATH set to:", os.environ["LD_LIBRARY_PATH"])

def install_udev_rules():
    # 安装 udev 规则
    try:
        print("Installing udev rules...")
        # 确保脚本路径正确
        udev_script_path = "/home/agilex/MLLM/MLLM_Limo_Car/pyorbbecsdk-main/scripts/install_udev_rules.sh"  # 绝对路径
        subprocess.run(['sudo', 'bash', udev_script_path], check=True)  # 执行 udev 安装脚本
        print("Reloading udev rules...")
        subprocess.run(['sudo', 'udevadm', 'control', '--reload-rules'], check=True)  # 重新加载 udev 规则
        subprocess.run(['sudo', 'udevadm', 'trigger'], check=True)  # 触发 udev 事件
    except subprocess.CalledProcessError as e:
        print(f"Error during udev setup: {e}")

def run_example():
    # 运行 depth_viewer.py 示例
    try:
        print("Running depth_viewer.py example...")
        example_script_path = os.path.join(os.getcwd(), 'examples', 'depth_viewer.py')
        subprocess.run(['python3', example_script_path], check=True)  # 执行示例脚本
    except subprocess.CalledProcessError as e:
        print(f"Error running depth_viewer.py: {e}")

def load_depth_camera_environment():
    setup_paths()  # 设置路径
    install_udev_rules()  # 安装和重载 udev 规则
    success = run_example()  # 运行深度相机
    return success  # 返回深度相机环境加载是否成功

if __name__ == '__main__':
    is_loaded = load_depth_camera_environment()  # 加载深度相机环境
    if is_loaded:
        print("Depth camera environment loaded successfully.")
    else:
        print("Failed to load depth camera environment.")




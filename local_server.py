# local_server.py

import os
import subprocess

def start_local_server():
    """
    启动一个服务于 now_images 目录的本地 HTTP 服务器。
    该服务器将运行在 localhost:8000 上。
    """
    # 获取当前工作目录的 now_images 路径
    now_images_dir = os.path.join(os.getcwd(), 'now_images')

    # 确保 now_images 目录存在
    if not os.path.exists(now_images_dir):
        os.makedirs(now_images_dir)
        print(f"已创建目录: {now_images_dir}")

    # 启动本地 HTTP 服务器，并将其设置为后台运行
    try:
        print("正在启动本地服务器，服务于 now_images 目录...")
        subprocess.Popen(['python3', '-m', 'http.server', '8888', '--directory', now_images_dir])
        print("本地服务器已启动，访问地址: http://localhost:8888/")
    except Exception as e:
        print(f"启动本地服务器时出错: {e}")

def main():
    """
    主函数，调用 start_local_server() 来启动本地服务器。
    """
    print("准备启动本地服务器...")
    start_local_server()

if __name__ == "__main__":
    main()

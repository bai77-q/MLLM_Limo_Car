# API_KEY.py

from dotenv import load_dotenv
import os

# 加载 .env 文件中的环境变量
load_dotenv()

# 零一万物大模型开放平台：基础指令的大模型
# https://platform.lingyiwanwu.com
YI_KEY = os.getenv('YI_KEY')

# 百度智能云千帆ModelBuilder：用来做语音识别语音转换的
# https://qianfan.cloud.baidu.com
QIANFAN_API_KEY = os.getenv('QIANFAN_API_KEY')
QIANFAN_SECRET_KEY = os.getenv('QIANFAN_SECRET_KEY')

# 百度智能云千帆AppBuilder-SDK
APPBUILDER_TOKEN = os.getenv('APPBUILDER_TOKEN')

# 腾讯云的语音合成模型
VOICE_SECRET_ID = os.getenv('VOICE_SECRET_ID')
VOICE_SECRET_KEY = os.getenv('VOICE_SECRET_KEY')

# COS 配置
COS_SECRET_ID = os.getenv('COS_SECRET_ID')
COS_SECRET_KEY = os.getenv('COS_SECRET_KEY')
COS_REGION = os.getenv('COS_REGION')
COS_BUCKET_NAME = os.getenv('COS_BUCKET_NAME')

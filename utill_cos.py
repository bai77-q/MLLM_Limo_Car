# cos.py
import qcloud_cos
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import logging
from API_KEY import *  # 导入你的 COS 配置信息

# 打印日志
# logging.basicConfig(level=logging.INFO)

# 配置COS客户端
config = CosConfig(Region=COS_REGION, SecretId=COS_SECRET_ID, SecretKey=COS_SECRET_KEY)
client = CosS3Client(config)

def upload_image(image_data, object_key):
    """
    上传图像数据到COS，并指定文件夹路径。

    :param image_data: 二进制图像数据。
    :param object_key: 上传后在COS中的对象键（文件名）。
    :return: 上传成功的图片URL或错误信息。
    """
    try:
        # 指定文件夹路径
        object_key = f'llm_api/{object_key}'

        # 直接上传二进制数据
        response = client.put_object(
            Bucket=COS_BUCKET_NAME,
            Body=image_data,
            Key=object_key,
            ContentType='image/jpeg'  # 设定内容类型
        )
        # 构建图片的访问URL
        image_url = f'https://{COS_BUCKET_NAME}.cos.{COS_REGION}.myqcloud.com/{object_key}'
        return image_url

    except Exception as e:
        logging.error(f"上传文件失败: {e}")
        return None
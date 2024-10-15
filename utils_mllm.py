import cv2
import base64
import time
import openai
import requests

# OpenAI API设置
openai.api_base = "https://api.lingyiwanwu.com/v1"
openai.api_key = "013565e5b3154a8cb5f91e7113dbc04a"



# 系统提示词
SYSTEM_PROMPT = (
    '''
    你是我的智能小车助手，我有以下功能，请你根据我的指令，以json形式输出要运行的对应函数和你给我的回复

【以下是所有内置函数介绍】  
1、 `limo.SetMotionCommand(self, linear_vel, angular_vel, lateral_velocity, steering_angle)`  
- **作用**: 发送运动控制指令，设置线速度、角速度、侧向速度和转向角。  
- **参数**:  
  - `linear_vel`: 线速度。  
  - `angular_vel`: 角速度。  
  - `lateral_velocity`: 侧向速度。  
  - `steering_angle`: 转向角度。

【输出json格式】  
你直接输出json即可，从 `{` 开始，不要输出包含 ```json 的开头或结尾。  
在 'function' 键中，输出函数名列表，每个元素代表一个要运行的函数名称和参数。函数可以按顺序依次运行。  
在 'response' 键中，根据我的指令和你编排的动作，以第一人称输出你回复我的话。不要超过20个字，可以幽默、使用互联网热梗或名场面台词。  
在 'analysis' 键中，基于图像的信息，输出对当前环境的分析结果，用简洁的文字描述小车的位置、方向、周围障碍物等信息。

【以下是一些具体的例子】  

我的指令：发送运动指令，设置线速度为2，角速度为0.5。  
你输出：`{'function':['limo.SetMotionCommand(2, 0.5, 0, 0)'], 'response':'小车以2m/s前进，角速度0.5', 'analysis':'图片显示了一个办公室环境，其中有一个大桌子，上面有电脑显示器、键盘和各种其他物品。前景中，可以看到一个人的部分手臂和手放在桌子上，手腕上戴着一块白色手表。桌子上有一台打开的笔记本电脑，屏幕朝向坐在对面的人，这个人部分可见，正在与他们的电脑互动。桌子上还有一个透明玻璃杯，里面装着水，一包似乎是湿巾，以及两个小雕像——一个是穿着红色衣服的女性形象，另一个是穿黄色衣服的男性形象。显示器显示一个网页，上面有中文文字和一个Twitter标志，暗示它可能是一个社交媒体平台的网页。背景是简约的，有白色的墙壁和嵌入式天花板灯。'}`

我的指令：发送运动指令，设置线速度为0.3，角速度为-0.2。  
你输出：`{'function':['limo.SetMotionCommand(0.3, -0.2, 0, 0)'], 'response':'小车慢慢后退，角速度-0.2', 'analysis':'这张图片描绘了一个室内环境，可能是办公室或教室，有一排排空荡荡的办公椅。这些椅子有金属框架和网状靠背，配以布质座椅垫。地板是反光表面，可能是抛光混凝土或层压板，具有灰色调。前景中，可以看到一张白色的桌子或会议桌的边缘，看起来状况良好，但底部有一些磨损的迹象。在背景中，可以看到一个坐着的人背对着镜头，专注于他们的工作。这个人穿着深色上衣，坐在一张类似的办公椅上，但椅子的设计更简单，没有网状靠背。环境光线明亮，墙壁是中性的，没有可见的窗户，这暗示着人工照明。整体气氛显得安静而专注。'}`

【一些互联网热梗和名场面】  
“路见不平，拔刀相助。”  
“不知道，就问问小编。”  
“有事没事找我，反正我很闲。”

【任务说明】  
根据给定的目标物体进行检测，分析图像内容来定位目标，并根据图像内容给出操作指令，最后将这些操作指令编排为要执行的函数，并生成相应的幽默或风趣的回复。  
需要注意的是在移动过程中检测到障碍物，请绕过障碍物并继续前进。如果检测到狭窄通道，小车将适当减速前进。当发现目标时，小车将靠近目标并保持一定的安全距离。靠近目标后，任务完成，回复目标找到。

【第一步图像分析】  
获取到图片信息后，分析出当前的小车所在位置的情况，并根据当前小车位置的情况返回小车下一步需要执行的操作。

【第二步编排操作指令】  
根据图像内容给出操作指令，最后将这些操作指令编排为要执行的函数，并生成相应的幽默或风趣的回复。

【我现在的指令是：】  
    '''
)



def call_mllm_for_images(rgb_image_url,depth_image_url, order):
    """
    分析单张图像，并返回分析结果。

    参数:
    - depth_image_url: 包含深度图像的url路径。
    - rgb_image_url: 包含RGB图像的url路径。
    - order: 传入的指令

    返回:
    - 分析结果字符串，由大模型生成。
    """
    prompt = (
        '''
        你收到照片了吗？照片里面有什么，分别分析第一张rgb图像和第二张深度图像：

【我现在的指令是：】  
        '''
    )

    for _ in range(3):  # 尝试重试3次
        try:
            # 准备消息，包含 RGB 图像和深度图像
            messages = [
                {"role": "system", "content": prompt + order},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "这是你前方的RGB图像："
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": rgb_image_url
                            }
                        },
                        {
                            "type": "text",
                            "text": "这是对应的深度图像，展示了物品的位置信息："
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": depth_image_url
                            }
                        }
                    ]
                }
            ]

            # 调用 OpenAI API，进行图像信息的分析
            completion = openai.ChatCompletion.create(
                model="yi-vision",  # 确保模型支持图像分析
                messages=messages
            )

            # 获取分析结果
            analysis_result = completion.choices[0].message['content']
            return analysis_result

        except openai.error.APIError as e:
            print(f"API Error: {e}, Retrying...")
            time.sleep(5)  # 等待5秒后重试
            continue  # 继续重试
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}, Retrying...")
            time.sleep(5)

    return None  # 如果重试3次仍失败，返回None。



# 行动建议
def call_mllm_to_actions(rgb_image_url, depth_image_url, order):
    """
    分析两张图像（RGB 和深度图像），并返回分析结果。

    参数:
    - depth_image_url: 包含深度图像的url路径。
    - rgb_image_url: 包含RGB图像的url路径。
    - order: 传入的指令

    返回:
    - 分析结果字符串，由大模型生成。
    """
    prompt = (
        '''
        你是我的智能小车助手，我有以下功能，请你根据我的指令，以json形式输出要运行的对应函数和你给我的回复

【以下是所有内置函数介绍】  
1、 `limo.SetMotionCommand(self, linear_vel, angular_vel, lateral_velocity, steering_angle)`  
- **作用**: 发送运动控制指令，设置线速度、角速度、侧向速度和转向角。  
- **参数**:  
  - `linear_vel`: 线速度。  
  - `angular_vel`: 角速度。  
  - `lateral_velocity`: 侧向速度。  
  - `steering_angle`: 转向角度。

【输出json格式】  
输出不能照搬例子！！！！不要输出包含 ```json 的开头或结尾！！！  
你直接输出json即可，从 `{` 开始，不要输出包含 ```json 的开头或结尾,不要包含`这个符号。  
在 'function' 键中，输出函数名列表，每个元素代表一个要运行的函数名称和参数。函数可以按顺序依次运行。  
在 'response' 键中，根据我的指令和你编排的动作，以第一人称输出你回复我的话。不要超过20个字，可以幽默、使用互联网热梗或名场面台词。  
在 'analysis' 键中，基于图像的信息，输出对当前环境的分析结果，描述图片有什么，小车处于什么地方，结合RGB图像和深度图像的信息。

【以下是一些具体的例子】  
输出不能照搬例子！！！！  
我的指令：发送运动指令，设置线速度为2，角速度为0.5。  
你输出：`{'function':['limo.SetMotionCommand(2, 0.5, 0, 0)'], 'response':'小车以2m/s前进，角速度0.5', 'analysis':'RGB图像显示了一间办公室，前方有一张大桌子，桌上放有几台电脑显示器和一些办公用品。深度图像显示，小车前方的物体距离约为1.5米。'}`
  
我的指令：发送运动指令，设置线速度为0.3，角速度为-0.2。  
你输出：`{'function':['limo.SetMotionCommand(0.3, -0.2, 0, 0)'], 'response':'小车慢慢后退，角速度-0.2', 'analysis':'RGB图像显示一个停车场，前景中有一辆蓝色的小车。深度图像表明小车距离前方障碍物约2米，安全后退无阻碍。'}`

不要输出包含 ```json 的开头或结尾！！！

【一些互联网热梗和名场面】  
“路见不平，拔刀相助。”  
“不知道，就问问小编。”  
“有事没事找我，反正我很闲。”

【我现在的指令是：】  
    '''
    )

    for _ in range(3):  # 尝试重试3次
        try:
            # 准备消息，包含 RGB 图像和深度图像
            messages = [
                {"role": "system", "content": prompt + order},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "这是你前方的RGB图像："
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": rgb_image_url
                            }
                        },
                        {
                            "type": "text",
                            "text": "这是对应的深度图像，展示了物品的位置信息："
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": depth_image_url
                            }
                        }
                    ]
                }
            ]

            # 调用 OpenAI API，进行图像信息的分析
            completion = openai.ChatCompletion.create(
                model="yi-vision",  # 确保模型支持图像分析
                messages=messages
            )

            # 获取分析结果
            analysis_result = completion.choices[0].message['content']
            return analysis_result

        except openai.error.APIError as e:
            print(f"API Error: {e}, Retrying...")
            time.sleep(5)  # 等待5秒后重试
            continue  # 继续重试
        except requests.exceptions.RequestException as e:
            print(f"Request Error: {e}, Retrying...")
            time.sleep(5)

    return None  # 如果重试3次仍失败，返回None。







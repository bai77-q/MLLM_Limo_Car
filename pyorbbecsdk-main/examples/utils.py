# ******************************************************************************
#  Copyright (c) 2023 Orbbec 3D Technology, Inc
#  
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.  
#  You may obtain a copy of the License at
#  
#      http:# www.apache.org/licenses/LICENSE-2.0
#  
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
# ******************************************************************************
from typing import Union, Any, Optional

from pyorbbecsdk import FormatConvertFilter, VideoFrame
from pyorbbecsdk import OBFormat, OBConvertFormat
import cv2
import numpy as np


def yuyv_to_bgr(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    yuyv = frame.reshape((height, width, 2))
    bgr_image = cv2.cvtColor(yuyv, cv2.COLOR_YUV2BGR_YUY2)
    return bgr_image


def uyvy_to_bgr(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    uyvy = frame.reshape((height, width, 2))
    bgr_image = cv2.cvtColor(uyvy, cv2.COLOR_YUV2BGR_UYVY)
    return bgr_image


def i420_to_bgr(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    y = frame[0:height, :]
    u = frame[height:height + height // 4].reshape(height // 2, width // 2)
    v = frame[height + height // 4:].reshape(height // 2, width // 2)
    yuv_image = cv2.merge([y, u, v])
    bgr_image = cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR_I420)
    return bgr_image


def nv21_to_bgr(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    y = frame[0:height, :]
    uv = frame[height:height + height // 2].reshape(height // 2, width)
    yuv_image = cv2.merge([y, uv])
    bgr_image = cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR_NV21)
    return bgr_image


def nv12_to_bgr(frame: np.ndarray, width: int, height: int) -> np.ndarray:
    y = frame[0:height, :]
    uv = frame[height:height + height // 2].reshape(height // 2, width)
    yuv_image = cv2.merge([y, uv])
    bgr_image = cv2.cvtColor(yuv_image, cv2.COLOR_YUV2BGR_NV12)
    return bgr_image


def determine_convert_format(frame: VideoFrame):
    if frame.get_format() == OBFormat.I420:
        return OBConvertFormat.I420_TO_RGB888
    elif frame.get_format() == OBFormat.MJPG:
        return OBConvertFormat.MJPG_TO_RGB888
    elif frame.get_format() == OBFormat.YUYV:
        return OBConvertFormat.YUYV_TO_RGB888
    elif frame.get_format() == OBFormat.NV21:
        return OBConvertFormat.NV21_TO_RGB888
    elif frame.get_format() == OBFormat.NV12:
        return OBConvertFormat.NV12_TO_RGB888
    elif frame.get_format() == OBFormat.UYVY:
        return OBConvertFormat.UYVY_TO_RGB888
    else:
        return None


def frame_to_rgb_frame(frame: VideoFrame) -> Union[Optional[VideoFrame], Any]:
    if frame.get_format() == OBFormat.RGB:
        return frame
    convert_format = determine_convert_format(frame)
    if convert_format is None:
        print("Unsupported format")
        return None
    print("covert format: {}".format(convert_format))
    convert_filter = FormatConvertFilter()
    convert_filter.set_format_convert_format(convert_format)
    rgb_frame = convert_filter.process(frame)
    if rgb_frame is None:
        print("Convert {} to RGB failed".format(frame.get_format()))
    return rgb_frame


def frame_to_bgr_image(frame: VideoFrame) -> Union[Optional[np.array], Any]:
    width = frame.get_width()
    height = frame.get_height()
    color_format = frame.get_format()
    data = np.asanyarray(frame.get_data())
    image = np.zeros((height, width, 3), dtype=np.uint8)
    if color_format == OBFormat.RGB:
        image = np.resize(data, (height, width, 3))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    elif color_format == OBFormat.BGR:
        image = np.resize(data, (height, width, 3))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    elif color_format == OBFormat.YUYV:
        image = np.resize(data, (height, width, 2))
        image = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_YUYV)
    elif color_format == OBFormat.MJPG:
        image = cv2.imdecode(data, cv2.IMREAD_COLOR)
    elif color_format == OBFormat.I420:
        image = i420_to_bgr(data, width, height)
        return image
    elif color_format == OBFormat.NV12:
        image = nv12_to_bgr(data, width, height)
        return image
    elif color_format == OBFormat.NV21:
        image = nv21_to_bgr(data, width, height)
        return image
    elif color_format == OBFormat.UYVY:
        image = np.resize(data, (height, width, 2))
        image = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_UYVY)
    else:
        print("Unsupported color format: {}".format(color_format))
        return None
    return image

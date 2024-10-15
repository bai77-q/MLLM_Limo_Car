
import base64
import json
import os
import wave
import pyaudio
import requests

API_KEY = "VtOJDzsN8rk5OsgesGQ4GI5b"
SECRET_KEY = "uJKeunrIrb4ZEAvblzILoVIu5mFCUfMa"

# 设置音频参数
CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 1  # 单通道
RATE = 16000  # 常见的采样率
RECORD_SECONDS = 8
OUTPUT_DIR = "MLLM_LIMO_CAR/output/voice_text"  # 文件夹名称

def ensure_output_dir():
    """确保输出目录存在"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def get_current_filename():
    """获取当前文件名，如果不存在则返回 voice_text1.wav"""
    ensure_output_dir()
    existing_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("voice_text") and f.endswith(".wav")]
    if not existing_files:
        return os.path.join(OUTPUT_DIR, "voice_text1.wav")
    else:
        max_num = max([int(f.split("voice_text")[1].split(".wav")[0]) for f in existing_files])
        return os.path.join(OUTPUT_DIR, f"voice_text{max_num}.wav")

def get_next_filename():
    """生成下一个文件名"""
    ensure_output_dir()
    existing_files = [f for f in os.listdir(OUTPUT_DIR) if f.startswith("voice_text") and f.endswith(".wav")]
    if not existing_files:
        return os.path.join(OUTPUT_DIR, "voice_text1.wav")
    else:
        max_num = max([int(f.split("voice_text")[1].split(".wav")[0]) for f in existing_files])
        return os.path.join(OUTPUT_DIR, f"voice_text{max_num + 1}.wav")

def record():
    """录音函数"""
    p = pyaudio.PyAudio()
    frames = []

    try:
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
        print("录音开始...")

        for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)

        print("录音结束。")

    except Exception as e:
        print(f"录音过程中发生错误：{e}")

    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()

    if frames:
        output_file = get_next_filename()
        print(f"正在将音频写入 {output_file}")
        try:
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(p.get_sample_size(FORMAT))
                wf.setframerate(RATE)
                wf.writeframes(b''.join(frames))
            print("音频写入成功。")
        except Exception as e:
            print(f"写入 WAV 文件时发生错误：{e}")
    else:
        print("未捕获到任何音频帧！")

def get_access_token():
    """获取百度Access Token"""
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": API_KEY, "client_secret": SECRET_KEY}
    response = requests.post(url, params=params)
    if response.ok:
        return response.json().get("access_token")
    else:
        print(f"Error fetching token: {response.text}")
        return None

def recognize_speech():
    """使用百度API进行语音识别"""
    current_file = get_current_filename()
    if not os.path.exists(current_file):
        print(f"文件 {current_file} 不存在，无法进行语音识别。")
        return

    token = get_access_token()
    if not token:
        print("无法获取token")
        return

    url = "https://vop.baidu.com/server_api"

    with open(current_file, 'rb') as f:
        audio_data = f.read()

    audio_base64 = base64.b64encode(audio_data).decode('utf-8')

    payload = json.dumps({
        "format": "wav",
        "rate": 16000,
        "channel": 1,
        "cuid": "w1Xl5WcuZ7rA9OLMxBxTm9nRhWJ631V1",
        "token": token,
        "speech": audio_base64,
        "len": len(audio_data)
    })

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)

    if response.ok:
        result = response.json().get("result", [])
        if result:
            return result[0]
        else:
            print("未识别到任何内容。")
            return None
    else:
        print("请求失败:", response.text)
        return None

if __name__ == "__main__":
    # 录音
    record()
    # 语音识别
    command = recognize_speech()
    if command:
        print(f"识别到的指令：{command}")
    else:
        print("未能识别到有效指令。")
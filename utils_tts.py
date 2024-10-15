import base64
import hashlib
import hmac
import json
import time
from datetime import datetime
from http.client import HTTPSConnection
import wave
import pyaudio

secret_id = "AKIDKWau76xiN0Vny67uvjcVYP2Xs8B3tUs2"
secret_key = "3tZzugNwJXZN0TimcO0QgrtnUyGTXQNQ"
token = ""

# 请求相关参数
service = "tts"
host = "tts.tencentcloudapi.com"
region = "ap-chengdu"
version = "2019-08-23"
action = "TextToVoice"
endpoint = "https://tts.tencentcloudapi.com"
algorithm = "TC3-HMAC-SHA256"

# 播放音频的函数
def play_audio_file(file_path):
    chunk = 1024
    wf = wave.open(file_path, 'rb')
    p = pyaudio.PyAudio()

    # 打开音频流
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # 读取并播放音频数据
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    # 关闭流和PyAudio
    stream.stop_stream()
    stream.close()
    p.terminate()

# 签名函数
def sign(key, msg):
    return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

# 生成语音并保存的函数
def generate_and_play_audio(text):
    # 时间戳和日期
    timestamp = int(time.time())
    date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

    # 拼接请求载荷
    payload = json.dumps({"Text": text, "SessionId": "session-1234"})

    # 拼接规范请求串
    http_request_method = "POST"
    canonical_uri = "/"
    canonical_querystring = ""
    ct = "application/json; charset=utf-8"
    canonical_headers = f"content-type:{ct}\nhost:{host}\nx-tc-action:{action.lower()}\n"
    signed_headers = "content-type;host;x-tc-action"
    hashed_request_payload = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    canonical_request = (http_request_method + "\n" +
                         canonical_uri + "\n" +
                         canonical_querystring + "\n" +
                         canonical_headers + "\n" +
                         signed_headers + "\n" +
                         hashed_request_payload)

    # 拼接待签名字符串
    credential_scope = f"{date}/{service}/tc3_request"
    hashed_canonical_request = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
    string_to_sign = (algorithm + "\n" +
                      str(timestamp) + "\n" +
                      credential_scope + "\n" +
                      hashed_canonical_request)

    # 计算签名
    secret_date = sign(("TC3" + secret_key).encode("utf-8"), date)
    secret_service = sign(secret_date, service)
    secret_signing = sign(secret_service, "tc3_request")
    signature = hmac.new(secret_signing, string_to_sign.encode("utf-8"), hashlib.sha256).hexdigest()

    # 拼接 Authorization
    authorization = (algorithm + " " +
                     "Credential=" + secret_id + "/" + credential_scope + ", " +
                     "SignedHeaders=" + signed_headers + ", " +
                     "Signature=" + signature)

    # 请求头
    headers = {
        "Authorization": authorization,
        "Content-Type": ct,
        "Host": host,
        "X-TC-Action": action,
        "X-TC-Timestamp": str(timestamp),
        "X-TC-Version": version
    }
    if region:
        headers["X-TC-Region"] = region
    if token:
        headers["X-TC-Token"] = token

    # 发起请求并处理响应
    try:
        req = HTTPSConnection(host)
        req.request("POST", "/", headers=headers, body=payload.encode("utf-8"))
        resp = req.getresponse()
        response_data = json.loads(resp.read().decode("utf-8"))

        # 获取Base64编码的WAV数据
        if 'Audio' in response_data['Response']:
            audio_base64 = response_data['Response']['Audio']

            # 解码并保存WAV文件
            audio_data = base64.b64decode(audio_base64)
            output_file = "voice_put.wav"
            with open(output_file, "wb") as wav_file:
                wav_file.write(audio_data)

            print("WAV文件已保存至", output_file)

            # 播放WAV文件
            play_audio_file(output_file)

        else:
            print("请求失败：未能获取音频数据")

    except Exception as err:
        print("发生错误:", err)

# 调用函数进行文本转换和播放
text_to_speech = "您好，我是Limo—002332。"
generate_and_play_audio(text_to_speech)
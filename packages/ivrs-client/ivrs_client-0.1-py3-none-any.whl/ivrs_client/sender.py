import os
import wave

import pyaudio
import numpy as np
import requests
from loguru import logger
from pydub import AudioSegment
from pydub.playback import play
from getmac import get_mac_address

class Sender:
    """集成语音发送和接收相关功能"""
    def __init__(self, url, audio_folder = "./audios", silence_duration=1.5, max_record_seconds=10):
        """
        初始化 Sender 对象

        参数:
            url (str): 服务器地址
            audio_folder (str): 存放录音的文件夹路径
            silence_duration (float): 静音检测时长
            max_record_seconds (int): 录音最大时长

        返回:
            None
        """

        # 服务器地址
        self.url = url
        # 采样率
        self.sample_rate = 16000
        # 每个 chunk 的大小
        self.chunk_size = 1024
        # 静音阈值
        self.silence_threshold = 200
        # 静音检测时长
        self.silence_duration = silence_duration
        # 录音最大时长
        self.max_record_seconds = max_record_seconds
        # 声道数
        self.channels = 1
        # 采样格式
        self.format = pyaudio.paInt16
        # 音频文件夹
        self.audio_folder = audio_folder
        # 本机 mac 地址
        self.mac_address = get_mac_address()
        # 检查存放录音的文件夹是否存在，不存在则创建
        if not os.path.exists(self.audio_folder):
            os.makedirs(self.audio_folder)

    # 参数是录音文件的存储路径
    def record_audio(self, file_name="input.wav"):
        """
        录音并自动检测静音提前结束，保存为 WAV 文件

        参数:
            file_name (str): 录音文件名

        返回:
            str: 录音文件名
        """

        file_path = self.audio_folder + f"/{file_name}"

        # 录音
        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.channels,
                        rate=self.sample_rate,
                        input=True,
                        frames_per_buffer=self.chunk_size)

        logger.info("开始录音，请开始说话...")

        frames = []
        silence_chunk_limit = int(self.silence_duration / (self.chunk_size / self.sample_rate))
        silence_count = 0
        total_chunks = int(self.sample_rate / self.chunk_size * self.max_record_seconds)

        for _ in range(total_chunks):
            data = stream.read(self.chunk_size)
            frames.append(data)

            # 静音检测
            audio_np = np.frombuffer(data, dtype=np.int16)
            volume = np.abs(audio_np).mean()
            if volume < self.silence_threshold:
                silence_count += 1
            else:
                silence_count = 0

            if silence_count >= silence_chunk_limit:
                logger.info(f"检测到持续静音 {self.silence_duration}s，提前结束录音")
                break

        logger.info("结束录音，正在保存文件...")

        stream.stop_stream()
        stream.close()
        p.terminate()

        # 保存为 wav 格式
        with wave.open(file_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.format))
            wf.setframerate(self.sample_rate)
            wf.writeframes(b''.join(frames))

        logger.info(f"音频已保存至：{file_path}")

        # 返回文件名称供后续使用
        return file_name

    def play_audio(self, file_name):
        """播放任意格式音频文件

        参数:
            file_name (str): 音频文件名

        返回:
            None
        """
        file_path = self.audio_folder + f"/{file_name}"
        logger.info(f"正在播放：{file_path}")
        audio = AudioSegment.from_file(file_path)
        play(audio)
        logger.info("播放完成")

    def recognize_audio(self, input_file_name = "input.wav"):
        """发送音频文件到后端服务器识别音频内容，接收合成结果

        参数:
            input_file_name (str): 输入音频文件名

        返回:
            str: 识别结果   
        """
        input_file_path = self.audio_folder + f"/{input_file_name}"
        server_url = self.url + "/Assistance/recognizeAudio"
        
        files = {
            "audioFile": (input_file_path, open(input_file_path, "rb"), "audio/wav")
        }

        try:
            logger.info("正在发送音频文件...")
            response = requests.post(server_url, files=files)

            if response.status_code == 200:
                return response.text
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容：{response.text}")
        except Exception as e:
            logger.error(f"请求出错：{e}")
        finally:
            # 确保文件在发送后关闭
            files['audioFile'][1].close()
        return "asr 请求失败"

    def get_llm_response(self, text):
        """发送文本到后端获取LLM响应

        参数:
            text (str): 要发送的文本内容
        
        返回:
            dict: LLM响应数据
        """
        server_url = self.url + "/Assistance/getLLMResponse"
        
        params = {
            "text": text,
            "macAddress": self.mac_address
        }

        try:
            logger.info("正在发送文本到LLM...")
            response = requests.get(server_url, params=params)

            if response.status_code == 200:
                response_data = response.json()
                logger.info("成功获取LLM响应")
                return response_data["value"]
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容：{response.text}")
                return None
        except Exception as e:
            logger.error(f"请求出错：{e}")
            return None

    def generate_audio(self, text, output_file_name="generated.mp3"):
        """
        发送文本到后端生成音频文件

        参数:
            text (str): 要转换为语音的文本
            output_file_name (str): 输出音频文件名
        
        返回:
            str: 生成的音频文件名
        """
        output_file_path = self.audio_folder + f"/{output_file_name}"
        server_url = self.url + "/Assistance/generateAudio"
        
        params = {
            "text": text
        }

        try:
            logger.info("正在发送文本生成音频...")
            response = requests.get(server_url, params=params)

            if response.status_code == 200:
                with open(output_file_path, "wb") as out:
                    out.write(response.content)
                logger.info(f"成功生成音频，已保存为：{output_file_path}")
                return output_file_name
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容：{response.text}")
                return None
        except Exception as e:
            logger.error(f"请求出错：{e}")
            return None

    
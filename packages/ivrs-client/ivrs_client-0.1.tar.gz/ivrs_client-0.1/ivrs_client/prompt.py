import os
import requests
from loguru import logger
from getmac import get_mac_address


class PromptHelper:
    """Prompt配置管理客户端，用于管理用户的Prompt设置"""
    
    def __init__(self, url):
        """
        初始化 PromptHelper 对象

        参数:
            url (str): 服务器地址
        """
        # 服务器地址
        self.url = url
        # 本机 mac 地址
        self.mac_address = get_mac_address()

    def get_prompt(self):
        """获取当前用户的Prompt配置

        返回:
            str: 当前用户的Prompt配置内容
        """
        server_url = self.url + "/Prompt/getPrompt"
        
        params = {
            "macAddress": self.mac_address
        }

        try:
            logger.info("正在获取用户Prompt配置...")
            response = requests.get(server_url, params=params)

            if response.status_code == 200:
                prompt_content = response.text
                logger.info("成功获取用户Prompt配置")
                return prompt_content
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容：{response.text}")
                return None
        except Exception as e:
            logger.error(f"请求出错：{e}")
            return None

    def create_prompt(self, prompt):
        """创建用户的Prompt配置

        参数:
            prompt (str): 要创建的Prompt内容
        
        返回:
            str: 创建结果信息
        """
        server_url = self.url + "/Prompt/createPrompt"

        try:
            logger.info("正在创建用户Prompt配置...")
            response = requests.post(
                server_url,
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "macAddress": self.mac_address
                }
            )

            if response.status_code == 200:
                result = response.text
                logger.info("成功创建用户Prompt配置")
                return result
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容：{response.text}")
                return None
        except Exception as e:
            logger.error(f"请求出错：{e}")
            return None

    def update_prompt(self, prompt):
        """更新用户的Prompt配置

        参数:
            prompt (str): 要更新的Prompt内容
        
        返回:
            str: 更新结果信息
        """
        server_url = self.url + "/Prompt/updatePrompt"

        try:
            logger.info("正在更新用户Prompt配置...")
            response = requests.post(
                server_url,
                headers={
                    "Content-Type": "application/json"
                },
                json={
                    "prompt": prompt,
                    "macAddress": self.mac_address
                }
            )

            if response.status_code == 200:
                result = response.text
                logger.info("成功更新用户Prompt配置")
                return result
            else:
                logger.error(f"请求失败，状态码: {response.status_code}")
                logger.error(f"响应内容：{response.text}")
                return None
        except Exception as e:
            logger.error(f"请求出错：{e}")
            return None
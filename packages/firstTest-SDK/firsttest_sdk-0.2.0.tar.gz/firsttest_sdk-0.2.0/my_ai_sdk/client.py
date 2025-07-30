# my_ai_sdk/client.py
import requests
import json
from typing import Dict, Any


class TestAIClient:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url

    def predict(self, image_path: str) -> Dict[str, Any]:
        """调用图像分类模型进行预测"""
        url = f"{self.base_url}/predict"

        with open(image_path, "rb") as f:
            files = {"image": f}
            response = requests.post(url, files=files)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API请求失败: {response.status_code}, {response.text}")


# 提供一个默认客户端
default_client = TestAIClient()
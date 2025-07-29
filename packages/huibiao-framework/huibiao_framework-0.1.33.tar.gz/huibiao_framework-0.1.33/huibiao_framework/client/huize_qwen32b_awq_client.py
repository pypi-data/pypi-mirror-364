import time
from typing import Optional

import aiohttp
from loguru import logger

from huibiao_framework.client.abstract_client import HuibiaoAbstractClient
from huibiao_framework.config.config import ModelConfig
from huibiao_framework.execption.vllm import (
    Qwen32bAwqResponseCodeError,
    Qwen32bAwqResponseFormatError,
)


class HuiZeQwen32bQwqClient(HuibiaoAbstractClient):
    """
    慧泽Qwen-32B模型客户端
    url: http://vllm-qwen-32b.model.hhht.ctcdn.cn:9080/common/query
    request:
        {
        "Action": "NormalChat",
        "DoSample": true,
        "Messages": [
                {
                    "content": "请将下面这段英文翻译成中文：请将下面这段英文翻译成中文：I am a test。",
                    "role": "user"
                }
            ]
        }
    response:
        {
            "code": 0,
            "result": {
                "Output": "我是一个测试。",
                "TokenProbs": [
                    1.0
                ]
            },
            "message": "success"
        }
    """

    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        super().__init__(
            client_name="HuiZeQwen32bQwq", session=session, url=ModelConfig.REQUEST_URL
        )

    async def query(self, prompt: str, session_id: str = "") -> Optional[str]:
        """发送查询请求到Qwen-32B模型（实例方法）"""

        session_tag = self.session_tag(session_id)

        # 处理过长prompt
        if len(prompt) > 16000:
            prompt = prompt[:7000] + prompt[-7000:]

        # 验证prompt有效性
        if not isinstance(prompt, str) or not prompt.strip():
            raise ValueError("Prompt must be a non-empty string")

        # 构建请求数据
        messages = [{"role": "user", "content": prompt}]
        data = {"Action": "NormalChat", "Messages": messages}

        start_time = time.time()
        try:
            # 发送异步POST请求
            async with self.session.post(self.url, json=data) as resp:
                sp_time = time.time() - start_time
                logger.debug(
                    f"{session_tag},resp-{resp.status},prompt len={len(prompt)},cost {sp_time:.2f}s"
                )
                resp.raise_for_status()
                response_data = await resp.json()

        except aiohttp.ClientError as e:
            logger.error(f"{session_tag} failed, {str(e)}")
            raise e

        # 解析响应结果
        code: int = response_data["code"]
        if code != 0:
            logger.error(f"{session_tag} resp error,code={code}")
            raise Qwen32bAwqResponseCodeError(code)
        if "result" not in response_data:
            logger.error(f"{session_tag} resp format error, field 'result' not found")
            raise Qwen32bAwqResponseFormatError("Field 'result' not found")
        if "Output" not in response_data["result"]:
            logger.error(f"{session_tag} resp format error, field 'result.Output' not found")
            raise Qwen32bAwqResponseFormatError("Field 'result.Output' not found")

        # 处理返回内容
        str_input = response_data["result"]["Output"]
        str_input = str_input.split("</think>")[-1]

        return str_input

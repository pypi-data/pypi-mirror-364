from .execption import HuiBiaoException


class Qwen32bAwqException(HuiBiaoException):
    pass


class Qwen32bAwqResponseFormatError(Qwen32bAwqException):
    def __init__(self, item: str):
        self.error_item = item
        super().__init__(f"模型返回结果格式错误，错误字段{self.error_item}")


class Qwen32bAwqResponseCodeError(Qwen32bAwqException):
    def __init__(self, code: int):
        self.code = code
        super().__init__(f"模型处理失败，code={self.code}!")

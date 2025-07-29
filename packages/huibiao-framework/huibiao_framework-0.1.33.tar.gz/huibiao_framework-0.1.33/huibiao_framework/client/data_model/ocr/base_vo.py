from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class OcrBaseRespVo(BaseModel, Generic[T]):

    # 响应状态码，0通常表示成功
    code: int = Field(..., description="响应状态码，0表示成功")

    # 响应消息
    message: str = Field("", description="响应状态描述信息")

    # 分析结果数据（泛型类型，可动态指定）
    result: Optional[T] = Field(None, description="分析结果数据，类型由泛型参数指定")

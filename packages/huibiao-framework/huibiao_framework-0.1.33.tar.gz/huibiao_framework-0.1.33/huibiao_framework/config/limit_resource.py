import os
from enum import Enum

from huibiao_framework.utils.meta_class import OsAttrMeta


class LimitResourceName(str, Enum):
    HUIZE_QWEN_32B_AWQ = "huizeQwen32bAwq"
    TENDER_IMAGE_OCR = "TenderImageOcr"
    TENDER_LAYOUT_DETECT = "TenderLayoutDetect"


class LimitResourceOsConfig(metaclass=OsAttrMeta):
    """
    有限资源访问限制的环境变量配置
    RES_MAX_NUM_{LimitResourceName} 资源最大访问数
    RES_ACQ_TIMES_{LimitResourceName} 尝试次数，获取锁失败不会消耗次数
    RES_RETRY_DELAY_{LimitResourceName} 重试等待秒数
    例如，qwen32b
    RES_MAX_NUM_HUIZE_QWEN_32B_AWQ=5
    RES_ACQ_TIMES_HUIZE_QWEN_32B_AWQ=20
    RES_RETRY_DELAY_HUIZE_QWEN_32B_AWQ=3
    """

    RES_MAX_NUM: int = 16
    RES_ACQ_TIMES: int = 20
    RES_RETRY_DELAY: int = 3

    @classmethod
    def get_res_max_num_os(cls, resource_name: str):
        return int(os.getenv(f"RES_MAX_NUM_{resource_name}", default=cls.RES_MAX_NUM))

    @classmethod
    def get_res_acq_times_os(cls, resource_name: str):
        return int(
            os.getenv(f"RES_ACQ_TIMES_{resource_name}", default=cls.RES_ACQ_TIMES)
        )

    @classmethod
    def get_res_retry_delay_os(cls, resource_name: str):
        return int(
            os.getenv(f"RES_RETRY_DELAY_{resource_name}", default=cls.RES_RETRY_DELAY)
        )

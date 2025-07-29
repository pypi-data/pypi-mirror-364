from loguru import logger

from .license import LimitResourceLicence
from huibiao_framework.redis_toolkit.client import HuibiaoAsyncRedisClientFactory
from huibiao_framework.config.limit_resource import (
    LimitResourceOsConfig,
    LimitResourceName,
)


class LimitResourceLicenseFactory:
    @classmethod
    def genLicense(
        cls,
        resource_name: str | LimitResourceName,
        user_info: str = None,
        max_num: int = None,
        acquire: int = None,
        delay: int = None,
    ) -> LimitResourceLicence:
        """
        获取指定资源的访问限制令牌
        """
        resource_name = (
            resource_name.name
            if isinstance(resource_name, LimitResourceName)
            else resource_name
        )
        max_num = (
            max_num
            if max_num is not None and max_num > 0
            else LimitResourceOsConfig.get_res_max_num_os(resource_name)
        )
        acquire = (
            acquire
            if acquire is not None and acquire > 0
            else LimitResourceOsConfig.get_res_acq_times_os(resource_name)
        )
        delay = (
            delay
            if delay is not None and delay > 0
            else LimitResourceOsConfig.get_res_retry_delay_os(resource_name)
        )
        logger.debug(
            f"Gen res license [{resource_name}][M={max_num}][A={acquire}][D={delay}]"
        )
        return LimitResourceLicence(
            resource_name=resource_name,
            redis_client=HuibiaoAsyncRedisClientFactory.get_client(),
            resource_max_num=max_num,
            acquire_times=acquire,
            retry_delay=delay,
            user_info=user_info,
        )

    @classmethod
    def HuiQwen32bAwqLicense(cls, user_info: str = None):
        return cls.genLicense(
            user_info=user_info, resource_name=LimitResourceName.HUIZE_QWEN_32B_AWQ
        )

    @classmethod
    def TenderImageOcrLicense(cls, user_info: str = None):
        return cls.genLicense(
            user_info=user_info, resource_name=LimitResourceName.TENDER_IMAGE_OCR
        )

    @classmethod
    def TenderLayoutDetectLicense(cls, user_info: str = None):
        return cls.genLicense(
            user_info=user_info, resource_name=LimitResourceName.TENDER_LAYOUT_DETECT
        )

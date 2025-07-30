# author: haoliqing
# date: 2023/9/5 15:24
# desc:
from abc import ABCMeta, abstractmethod
from device.base_device import Device
from typing import List, Any


class TemplatesInfo:
    def __init__(self):
        self.error_code: int = 0
        """错误码，该值不会返回给交易，仅用于标识读卡是否成功，小于0则表示失败，否则为成功，默认为0"""
        self.data: Any = None
        """返回的数据"""


class FingerScanner(Device, metaclass=ABCMeta):
    """指纹仪驱动适配器基类"""

    @abstractmethod
    def get_finger_template(self, finger_num: int) -> TemplatesInfo:
        """
        获取指纹模板
        :param finger_num: 获取指纹模板的数量
        :return: 指纹模板列表， 为None则获取失败
        """

    @abstractmethod
    def get_finger_feature(self) -> str:
        """
        获取指纹特征
        :return: 返回指纹特征，为 None则获取失败
        """

    @abstractmethod
    def verify_finger(self, template_list: List[str]) -> int:
        """
        读取并验证指纹
        :param template_list: 指纹模板列表
        :return: 执行结果，小于0为执行失败，否则为执行成功
        """
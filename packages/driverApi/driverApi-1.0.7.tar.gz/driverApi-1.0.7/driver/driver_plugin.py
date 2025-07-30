# author: haoliqing
# date: 2024/7/23 10:55
# desc:
from abc import ABCMeta, abstractmethod
from typing import List

from device.device_class_def import DeviceClass


class DriverPlugin(metaclass=ABCMeta):

    @abstractmethod
    def get_suitable_device_class_list(self) -> List[DeviceClass]:
        """
        获取该驱动适配的设备类型列表
        """
        pass

    @abstractmethod
    def get_suitable_device_model(self) -> str:
        """
        获取该驱动适配的设备型号
        """
        pass



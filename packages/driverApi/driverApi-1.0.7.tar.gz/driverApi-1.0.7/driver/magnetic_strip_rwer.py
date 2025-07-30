# author: haoliqing
# date: 2023/9/6 17:41
# desc:
from abc import ABCMeta, abstractmethod
from device.base_device import Device
from typing import List


class MagneticStripInfo(object):
    """磁条卡信息定义"""

    def __init__(self):
        self.err_code: int = 0
        """错误码，该值不会返回给交易，仅用于标识读卡是否成功，小于0则表示失败，否则为成功，默认为0"""

        self.card_no = None
        """卡号"""

        self.stack1_info = None
        """一磁道数据"""

        self.stack2_info = None
        """二磁道数据"""

        self.stack3_info = None
        """三磁道数据"""

    def __str__(self) -> str:
        return (f'MagneticStripInfo("card_no": {self.card_no},"first_track": {self.stack1_info},'
                f'"second_track": {self.stack2_info},"third_track": {self.stack3_info})')


class MagneticStripRWer(Device, metaclass=ABCMeta):
    """磁条卡读写器适配器基类"""

    @abstractmethod
    def read(self) -> MagneticStripInfo:
        """
        读取磁条信息
        :return: 读取到的信息，若返回值为None，则获取失败，否则读卡的成功与失败由MagneticStripInfo.errorCode来决定，
        若该值小于0，则认为读卡失败，否则为读卡成功，该值需要在驱动实现中自行设置，默认为0
        """
        pass

    @abstractmethod
    def write(self, stack1_info: str, stack2_info: str, stack3_info: str) -> int:
        """
        向磁条写入数据
        :param stack1_info: 要写入的一磁道数据，为None则不写入
        :param stack2_info: 要写入的二磁道数据，为None则不写入
        :param stack3_info: 要写入的三磁道数据，为None则不写入
        :return: 执行结果，小于0为执行失败，否则为执行成功
        """
        pass

# author: haoliqing
# date: 2024/5/8 11:32
# desc:
from device.base_device import Device
from abc import ABCMeta, abstractmethod
from typing import List, Dict


class SingleFilePrintResult(object):
    """生成ARQC时使用的交易数据"""

    def __init__(self):
        self.error_code: int = 0
        """错误码，该值不会返回给交易，仅用于标识文件打印是否成功，小于0则表示失败，否则为成功，默认为0"""

        self.error_msg: str = None
        """错误原因描述"""

    def __str__(self):
        return self.__dict__


class MultiFilePrintResult(object):
    """生成ARQC时使用的交易数据"""

    def __init__(self):
        self.error_code: int = 0
        """错误码，该值不会返回给交易，仅用于标识文件打印是否成功，小于0则表示失败，否则为成功，默认为0"""

        self.success_list: List[str] = None
        """成功文件列表"""

        self.fail_list: List[str] = None
        """失败文件列表"""

        self.error_msg: str = None
        """错误原因描述"""

    def __str__(self):
        return self.__dict__


class FilePrinter(Device, metaclass=ABCMeta):

    @abstractmethod
    def print_single_file(self, file_path: str) -> SingleFilePrintResult:
        """
        打印单个文件
        :param file_path: 文件绝对路径
        :return: 打印结果   小于0：失败   其他：成功
        """

    @abstractmethod
    def print_multi_file(self, file_path_list: List[str]) -> MultiFilePrintResult:
        """
        打印单个文件
        :param file_path_list: 文件绝对路径列表
        :return: 打印结果
        """

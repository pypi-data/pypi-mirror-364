# author: haoliqing
# date: 2023/8/16 14:30
# desc: 端口定义抽象类
from abc import ABCMeta, abstractmethod
from enum import Enum, unique


@unique
class PortType(Enum):
    """ 端口类型枚举类 """
    COM = 'COM'  # 串口
    LPT = 'LPT'  # 并口
    USB = 'USB'  # U口
    ETH = 'ETH'  # 网口
    MOCK = 'MOCK'  # 模拟端口
    SHARE = 'SHARE'  # 共享外设客户端端口
    BT = 'BT'  # 蓝牙连接


class Port(object, metaclass=ABCMeta):

    def __init__(self, port_id, port_param):
        self.__port_id = port_id
        self.__portParam: dict = port_param

    @property
    def port_id(self):
        return self.__port_id

    @port_id.setter
    def port_id(self, port_id):
        self.__port_id = port_id

    @abstractmethod
    def get_port_param_str(self):
        pass

    @abstractmethod
    def get_port_param(self, param_id):
        pass

    @abstractmethod
    def get_port_type(self) -> PortType:
        pass

# author: haoliqing
# date: 2023/9/5 15:24
# desc:
from abc import ABCMeta, abstractmethod
from device.base_device import Device


class KeyPadInfo:
    def __init__(self, error_code=0, data=None):
        self.error_code: int = error_code
        """错误码，该值不会返回给交易，仅用于标识读卡是否成功，小于0则表示失败，否则为成功，默认为0"""

        self.data: str = data


class KeyPad(Device, metaclass=ABCMeta):
    """数字键盘驱动适配器基类"""

    @abstractmethod
    def read_pwd(self, flag: int) -> KeyPadInfo:
        """
        读取密码，具体读取明文密码还是软/硬加密密码，在具体的驱动实现中处理
        :param flag: 读取密码类型: 1-密码，2-确认密码
        :return: 密码字符串，返回None则表示读取密码失败
        """

    @abstractmethod
    def set_master_key(self, old_key: str, new_key: str) -> int:
        """
        设置主密钥
        :param old_key: 原主密钥
        :param new_key:  新主密钥
        :return: 执行结果，小于0为执行失败，否则为执行成功
        """

    @abstractmethod
    def set_work_key(self, work_key: str) -> int:
        """
        设置工作密钥
        :param work_key: 工作密钥
        :return: 执行结果，小于0为执行失败，否则为执行成功
        """

# author: haoliqing
# date: 2024/1/2 16:34
# desc:

from abc import ABCMeta, abstractmethod

from driver.keypad import KeyPad, KeyPadInfo


class MultiFuncKeyPad(KeyPad, metaclass=ABCMeta):

    @abstractmethod
    def read_tel_no(self) -> KeyPadInfo:
        """
        读取输入的电话号码
        :return: 电话号码
        """
        pass

    @abstractmethod
    def read_auth_code(self) -> KeyPadInfo:
        """
        读取输入的验证码
        :return: 验证码
        """
        pass

# author: haoliqing
# date: 2024/8/2 14:44
# desc:

from abc import ABCMeta, abstractmethod

from device.base_device import Device


class SharedDeviceClient(Device, metaclass=ABCMeta):

    @abstractmethod
    def call_shared_device(self, request_data: str):
        """
        调用共享外设
        """

    @abstractmethod
    def retry(self, request_data: str):
        """
        通知共享外设重试任务（用户选择手动重试）
        """

    @abstractmethod
    def finish(self, request_data: str):
        """
        通知共享外设结束任务（用户取消手动重试）
        """

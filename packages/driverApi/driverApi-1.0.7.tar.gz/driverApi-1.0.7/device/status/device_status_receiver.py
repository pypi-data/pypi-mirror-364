# author: haoliqing
# date: 2023/11/1 15:55
# desc:
from abc import ABCMeta, abstractmethod
from typing import List

from common import Singleton
from device.status.device_status import DeviceStatus


class DeviceStatusListener(object, metaclass=ABCMeta):
    """设备状态变化监听器接口，用于将设备状态的变化通知给需要使用的地方"""

    @abstractmethod
    def on_status_change(self, status: DeviceStatus):
        pass


@Singleton
class DeviceStatusReceiver(object):
    """设备状态收集器，用于接收设备主动通知的状态变化"""

    def __init__(self):
        self.__status_listeners: List[DeviceStatusListener] = []

    def notify_status(self, status: DeviceStatus):
        for listener in self.__status_listeners:
            listener.on_status_change(status)

    def add_status_listener(self, listener: DeviceStatusListener):
        self.__status_listeners.append(listener)




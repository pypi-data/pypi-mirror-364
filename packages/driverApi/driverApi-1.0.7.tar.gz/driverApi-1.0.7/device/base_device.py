# author: haoliqing
# date: 2023/9/5 10:01
# desc:
from abc import ABCMeta

from device.device_config import DeviceConfig
from device.status.device_status import DeviceStatus, DeviceStatusType
from device.status.device_status_receiver import DeviceStatusReceiver


class Device(object, metaclass=ABCMeta):
    """ 设备驱动适配器基类，该基类定义了一个通用的设备使用方式，不同类型的设备通过扩充该接口增加功能 """

    def __init__(self):
        self.__is_busy = False
        self.__device_cfg = None
        self.__inited = False
        self.__status_receiver: DeviceStatusReceiver = DeviceStatusReceiver()

    def init(self, device_cfg: DeviceConfig) -> int:
        """
        初始化驱动适配器，通过该方法对适配器自身和设备驱动进行初始化
        :param device_cfg: 该设备对应的设备配置信息
        :return 执行结果，小于0为失败，否则为成功
        """
        if not self.__inited:
            self.__device_cfg = device_cfg
            self.__inited = True
        return 0

    def open(self) -> int:
        """
        打开和设备之间的会话
        :return: 执行结果，小于0为失败，否则为成功
        """
        self.__is_busy = True
        if self.__device_cfg:
            status = DeviceStatus(DeviceStatusType.DEV_BUSY, self.__device_cfg)
            self.__status_receiver.notify_status(status)
        return 0

    def close(self) -> int:
        """
        关闭和设备之间的会话
        :return: 执行结果，小于0为失败，否则为成功
        """
        self.__is_busy = False
        if self.__device_cfg:
            status = DeviceStatus(DeviceStatusType.DEV_READY, self.__device_cfg)
            self.__status_receiver.notify_status(status)
        return 0

    def get_status(self) -> DeviceStatus | None:
        """
        获取设备状态
        :return: 设备状态
        """
        if self.__device_cfg:
            if self.__is_busy:
                return DeviceStatus(DeviceStatusType.DEV_BUSY, self.__device_cfg)
            else:
                return DeviceStatus(DeviceStatusType.DEV_READY, self.__device_cfg)
        else:
            return None

    def is_cancel(self) -> bool:
        """
        设备是否支持取消任务
        @return:
        """
        return False

    def cancel(self) -> int:
        """
        取消任务
        @return:
        """
        return 0

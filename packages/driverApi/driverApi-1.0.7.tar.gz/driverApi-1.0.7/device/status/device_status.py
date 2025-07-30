# author: haoliqing
# date: 2023/9/5 11:14
# desc:
from enum import Enum, unique
import time

from device.device_config import DeviceConfig


@unique
class DeviceStatusType(Enum):
    """ 任务状态枚举类 """
    DEV_READY = 0  # 设备状态_就绪
    DEV_INIT = 1  # 设备状态_初始化
    DEV_BUSY = 2  # 设备状态_忙碌
    DEV_ERROR = 3  # 设备状态_错误
    DEV_UNINSTALL = 4  # 设备状态_未安装
    DEV_UNKNOWN = 5  # 设备状态_未知
    DEV_NOT_ONLINE = 6  # 设备状态_离线


class DeviceStatus(object):
    """设备状态定义"""

    valid_period = 3000

    def __init__(self, status_type: DeviceStatusType, dev_cfg: DeviceConfig):
        self.status_type = status_type
        self.dev_class = dev_cfg.device_class
        self.dev_class_desc = dev_cfg.device_class_desc
        self.dev_model = dev_cfg.device_model
        self.dev_model_desc = dev_cfg.device_model_desc
        self.valid_time = int(time.time() * 1000) + self.valid_period

    def is_valid(self) -> bool:
        if self.valid_time == 0 or self.valid_time > int(time.time() * 1000):
            return True
        else:
            return False

    def __str__(self) -> str:
        return f"[{self.status_type},{self.dev_class},{self.dev_class_desc},{self.dev_model},{self.dev_model_desc},{self.valid_time}]"

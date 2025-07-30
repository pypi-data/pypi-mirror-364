# author: haoliqing
# date: 2023/8/16 14:30
# desc: 设备配置定义类，该类定义了单个设备类型+设备型号的配置信息
from enum import unique, Enum

from common import global_constants
from device.device_class_def import DeviceClass
from device.port import Port, ComPort, MockPort, LptPort, EthPort, UsbPort,BtPort, PortType, SharedDevicePort
from logger.device_logger import logger


@unique
class DeviceConfigStatusType(Enum):
    """ 任务状态枚举类 """
    ENABLE = 1  # 设备绑定状态_启用
    DISABLE = 2  # 设备绑定状态_禁用
    ALTERNATIVE = 3  # 设备绑定状态_备选


class DeviceConfig(object):
    """设备配置定义类"""

    def __init__(self, dev_cfg: dict):
        self.__dev_cfg = dev_cfg
        self.__dev_class = dev_cfg[global_constants.DEV_CLASS_NAME]
        self.__dev_class_desc = dev_cfg[global_constants.DEV_CLASS_DESC]
        self.__dev_model = dev_cfg[global_constants.DEV_MODEL_NAME]
        self.__dev_model_desc = dev_cfg[global_constants.DEV_MODEL_DESC]
        self.__dev_model_param: dict = dev_cfg.get(global_constants.DEV_PARAM, None)
        self.__term_id = dev_cfg[global_constants.TERM_ID]
        self.__dev_status = dev_cfg[global_constants.DEV_STATUS]
        self.__is_default = dev_cfg.get(global_constants.DEFAULT, False)
        self.__port_cfg = dev_cfg.get(global_constants.PORT, None)
        self.__create_port(self.__port_cfg)

    @property
    def device_class(self) -> str:
        return self.__dev_class

    @property
    def device_model(self) -> str:
        return self.__dev_model

    @property
    def device_class_desc(self) -> str:
        return self.__dev_class_desc

    @property
    def device_model_desc(self) -> str:
        return self.__dev_model_desc

    @property
    def device_model_param(self) -> dict:
        return self.__dev_model_param

    @property
    def term_id(self) -> str:
        return self.__term_id

    @property
    def dev_status(self) -> str:
        return self.__dev_status

    @property
    def is_default(self) -> str:
        return self.__is_default

    @property
    def port(self) -> Port:
        return self.__port

    def __create_port(self, port_cfg):
        if self.__dev_class == DeviceClass.SHARED_DEVICE_CLIENT.value:
            self.__port = SharedDevicePort(None, None)
        if not port_cfg:
            # 没有端口配置，则认为是虚拟端口
            self.__port = MockPort(None, None)
        else:
            port_type = port_cfg[global_constants.COMM_TYPE_NAME]
            port_name = port_cfg[global_constants.COMM_PORT]
            port_param = port_cfg.get(global_constants.COMM_PORT_PARAM, {})
            if port_type == PortType.COM.value:
                self.__port = ComPort(port_name, port_param)
            elif port_type == PortType.LPT.value:
                self.__port = LptPort(port_name, port_param)
            elif port_type == PortType.USB.value:
                self.__port = UsbPort(port_name, port_param)
            elif port_type == PortType.ETH.value:
                self.__port = EthPort(port_name, port_param)
            elif port_type == PortType.BT.value:
                self.__port = BtPort(port_name, port_param)
            else:
                logger.error("不支持的端口类型{0}".format(port_type))

# author: haoliqing
# date: 2023/8/16 14:30
# desc: 设备配置管理类
import traceback
from typing import List, Dict, Set

from common import Singleton, global_constants
from device.device_config import DeviceConfig, DeviceConfigStatusType
from logger.device_logger import logger


@Singleton
class DeviceConfigManager(object):
    """设备配置管理类"""

    device_cfgs: Dict[str, Dict[str, DeviceConfig]] = {}
    """ 设备配置 {设备类型:{设备型号:设备配置信息}}"""

    cfgs_list: List[DeviceConfig] = []

    port_set: set = set()

    def init_dev_cfg(self, dev_cfg: Dict) -> bool:
        """
        初始化设备配置信息
        :param dev_cfg: 设备配置信息数据，其格式为 {设备类型:[类型下设备型号绑定信息列表]}
        :return: 是否初始化成功
        """
        self.device_cfgs.clear()
        self.cfgs_list.clear()
        try:
            for key in dev_cfg.keys():
                self.device_cfgs[key] = {}
                for cfg in dev_cfg[key]:
                    device_config = DeviceConfig(cfg)
                    if int(device_config.dev_status) == DeviceConfigStatusType.ENABLE.value:
                        self.device_cfgs[key][cfg[global_constants.DEV_MODEL_NAME]] = device_config
                        self.cfgs_list.append(device_config)
            return True
        except Exception as e:
            logger.error("初始化设备配置发生异常: {0}, 异常信息：{1}".format(str(e), traceback.format_exc()))
            self.device_cfgs.clear()
            return False

    def get_all_device_cfgs(self) -> Dict[str, Dict[str, DeviceConfig]]:
        """获取所有设备配置"""
        return self.device_cfgs

    def get_cfgs_list(self) -> List[DeviceConfig]:
        return self.cfgs_list

    def get_device_cfg(self, device_class: str, device_model: str) -> DeviceConfig:
        """根据设备类型和设备型号获取设备配置信息"""
        cfgs = self.device_cfgs.get(device_class, None)
        if cfgs:
            return cfgs.get(device_model, None)
        else:
            return None

    def get_device_cfgs_by_classes(self, device_class_list: List[str]) -> List[DeviceConfig]:
        """ 根据可选设备类型列表查找所有启用的设备 """
        result = []
        for cls in device_class_list:
            cfgs = self.device_cfgs.get(cls, None)
            if cfgs:
                result += cfgs.values()
        return result

    def get_all_ports(self) -> Set[str]:
        """获取绑定设备的所有端口号"""
        if len(self.port_set) == 0:
            for cls_cfg in self.device_cfgs.values():
                for model_cfg in cls_cfg.values():
                    port_name = model_cfg.port.port_id
                    self.port_set.add(port_name)
        return self.port_set



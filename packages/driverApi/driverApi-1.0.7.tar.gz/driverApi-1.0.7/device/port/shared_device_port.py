# author: haoliqing
# date: 2023/8/16 14:30
# desc: 共享外设客户端端口定义类，外设配置为指定端口的时候默认是模拟端口
from device.port.port import Port, PortType


class SharedDevicePort(Port):
    
    def get_port_type(self) -> PortType:
        return PortType.SHARE

    def __init__(self, port_name, port_param):
        super().__init__('shared_device_port', None)

    def get_port_param(self, param_id):
        return None

    def get_port_param_str(self):
        return None

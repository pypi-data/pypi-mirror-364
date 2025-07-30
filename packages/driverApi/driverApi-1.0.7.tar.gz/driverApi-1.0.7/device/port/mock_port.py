# author: haoliqing
# date: 2023/8/16 14:30
# desc: 模拟端口定义类，外设配置未指定端口的时候默认是模拟端口
from device.port.port import Port, PortType


class MockPort(Port):
    
    def get_port_type(self) -> PortType:
        return PortType.MOCK

    def __init__(self, port_name, port_param):
        super().__init__('mock_port', None)

    def get_port_param(self, param_id):
        return None

    def get_port_param_str(self):
        return None

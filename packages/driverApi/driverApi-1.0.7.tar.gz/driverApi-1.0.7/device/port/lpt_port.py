# author: haoliqing
# date: 2023/9/28 16:42
# desc:
from device.port.port import PortType, Port


class LptPort(Port):

    def __init__(self,  port_name, port_param):
        super().__init__('LPT', port_param)

    def get_port_param_str(self):
        pass

    def get_port_param(self, param_id):
        pass

    def get_port_type(self) -> PortType:
        return PortType.LPT
    
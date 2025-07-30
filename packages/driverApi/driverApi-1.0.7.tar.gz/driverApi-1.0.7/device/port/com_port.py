# author: haoliqing
# date: 2023/9/28 16:42
# desc:
from device.port.port import PortType, Port


class ComPort(Port):

    def __init__(self, port_name, port_param):
        self.port_name: str = port_name
        self.port_param: dict = port_param
        super().__init__(port_name, port_param)

    def get_port_param_str(self):
        pass

    def get_port_param(self, param_id):
        return self.port_param.get(param_id)

    def get_port_type(self) -> PortType:
        return PortType.COM

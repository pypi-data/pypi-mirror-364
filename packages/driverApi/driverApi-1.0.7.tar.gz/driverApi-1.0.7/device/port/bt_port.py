from device.port.port import PortType, Port


class BtPort(Port):

    def __init__(self, port_name, port_param):
        super().__init__("BT", port_param)

    def get_port_param_str(self):
        pass

    def get_port_param(self, param_id):
        pass

    def get_port_type(self) -> PortType:
        return PortType.BT

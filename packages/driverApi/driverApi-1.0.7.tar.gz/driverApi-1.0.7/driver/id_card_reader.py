# author: haoliqing
# date: 2023/9/6 16:49
# desc:
from abc import ABCMeta, abstractmethod
from device.base_device import Device


class IDInfo(object):
    """身份证信息定义类"""

    def __init__(self):
        self.err_code: int = 0
        """错误码，该值不会返回给交易，仅用于标识读卡是否成功，小于0则表示失败，否则为成功，默认为0"""

        self.id: str = None
        """身份证号码"""

        self.cnName: str = None
        """姓名"""

        self.sex: str = None
        """性别"""

        self.nation: str = None
        """民族"""

        self.birthday: str = None
        """出生日期"""

        self.address: str = None
        """居住地址"""

        self.dep: str = None
        """发证机关"""

        self.begin: str = None
        """生效日期"""

        self.end: str = None
        """截至日期"""

        self.image_path: str = None
        """身份证头像存储绝对路径"""

        self.image_info: str = None
        """身份证头像BASE64数据"""

    def __str__(self) -> str:
        return (f"IDInfo(\"cnName\":{self.cnName},\"nation\":{self.nation},\"birthday\":{self.birthday},"
                f"\"address\":{self.address},\"id\":{self.id},\"dep\":{self.dep},\"begin\":{self.begin},"
                f"\"end\":{self.end},\"image_path\":{self.image_path},\"imageInfo\":{self.image_info})")


class IDCardReader(Device, metaclass=ABCMeta):
    """身份证阅读器适配器基类"""

    @abstractmethod
    def read(self) -> IDInfo:
        """
        读取二代证信息
        :return: 读取到的二代证信息，若返回值为None，则获取失败，否则读卡的成功与失败由IDInfo.errorCode来决定，
        若该值小于0，则认为读卡失败，否则为读卡成功，该值需要在驱动实现中自行设置，默认为0
        """

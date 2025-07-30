# author: haoliqing
# date: 2023/9/5 15:24
# desc:
from abc import ABCMeta, abstractmethod
from device.base_device import Device


class EvaluateInfo(object):
    """评价信息定义"""

    def __init__(self):
        self.err_code: int = 0
        """错误码，该值不会返回给交易，仅用于标识读卡是否成功，小于0则表示失败，否则为成功，默认为0"""

        self.level = None
        """评价级别"""

        self.message = None
        """评价信息"""

    def __str__(self) -> str:
        return f'EvaluateInfo("level": {self.level},"message": {self.message})'


class Evaluator(Device, metaclass=ABCMeta):
    """评价器驱动适配器基类"""

    @abstractmethod
    def get_evaluate_result(self, teller_id: str, teller_name: str, teller_photo: str, star_level: int) -> EvaluateInfo:
        """
        读取评价结果
        :param teller_id:    柜员编号
        :param teller_name:   柜员姓名
        :param teller_photo:   柜员头像文件名
        :param star_level:   评价星级
        :return: 读取到的评价信息，若返回值为None，则获取失败，否则读取评价信息的成功与失败由EvaluateInfo.errorCode来决定，
        若该值小于0，则认为读取评价信息失败，否则为成功，该值需要在驱动实现中自行设置，默认为0
        """

    @abstractmethod
    def update_teller_photo(self, file_path: str) -> int:
        """
        更新柜员头像
        :param file_path: 更新的头像文件路径
        :return: 更新结果， 小于0：失败   其他：成功
        """

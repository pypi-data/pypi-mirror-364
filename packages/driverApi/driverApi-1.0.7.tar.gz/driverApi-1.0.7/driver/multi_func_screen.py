# author: haoliqing
# date: 2024/1/2 19:44
# desc:

from abc import ABCMeta, abstractmethod
from enum import unique, Enum

from device.base_device import Device


@unique
class FileType(Enum):
    """ 下载文件类型枚举类 """
    ADVERTISING = 0  # 广告
    VIDEO = 1  # 视频
    PHOTO = 2  # 柜员头像
    VOICE = 3  # 语音
    UPGRADE = 4  # 升级包


class SignInfo(object):
    """签名信息定义"""

    def __init__(self):
        self.err_code: int = 0
        """错误码，该值不会返回给交易，仅用于标识签名是否成功，小于0则表示失败，否则为成功，默认为0"""

        self.sign_data = None
        """签名笔迹数据"""

        self.sign_image_base64 = None
        """签名图片base64编码"""

    def __str__(self) -> str:
        return f'SignInfo("sign_data": {self.sign_data},"sign_image_base64": {self.sign_image_base64})'


class MultiFuncScreen(Device, metaclass=ABCMeta):
    """多功能屏幕适配器基类"""

    @abstractmethod
    def show_tran_info(self, info: str, param: str) -> int:
        """
        显示信息，仅显示信息，无需确认
        :param info: 需要展示的信息
        :param param:  自定义参数
        :return: 是否显示成功，小于0为失败，否则为成功
        """

    @abstractmethod
    def confirm_tran_info(self, info: str, param: str) -> int:
        """
        确认信息
        :param info: 需要展示的信息
        :param param:  自定义参数
        :return: 确认结果  0-确认  1-取消  2-超时   小于0-执行失败
        """

    @abstractmethod
    def request_sign(self, file_path: str, param: str) -> SignInfo:
        """
        请求签名
        :param file_path: 请求签名的文件路径
        :param param: 自定义参数
        :return: 签名信息，若返回值为None，则获取失败，否则读取签名信息的成功与失败由SignInfo.errorCode来决定，
        若该值小于0，则认为读取签名信息失败，否则为成功，该值需要在驱动实现中自行设置，默认为0
        """

    @abstractmethod
    def confirm_sign(self, file_path: str, param: str) -> int:
        """
        确认签名
        :param file_path: 请求确认的已合成签名的文件路径
        :param param: 自定义参数
        :return: 确认结果  0-确认  1-取消  2-超时   小于0-执行失败
        """

    @abstractmethod
    def download_file(self, file_type: FileType, file_path: str) -> int:
        """
        下载文件到设备
        :param file_type: 下载的文件类型
        :param file_path: 下载的文件路径
        :return: 是否下载成功，小于0为失败，否则为成功
        """

    @abstractmethod
    def delete_file(self, file_type: FileType, file_name: str) -> int:
        """
        删除设备上的文件
        :param file_type: 要删除的文件类型
        :param file_name: 要删除的文件名
        :return: 是否删除成功，小于0为失败，否则为成功
        """
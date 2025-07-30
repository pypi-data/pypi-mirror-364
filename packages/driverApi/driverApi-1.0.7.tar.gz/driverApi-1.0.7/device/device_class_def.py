# author: haoliqing
# date: 2024/7/23 11:16
# desc:
from enum import unique, Enum


@unique
class DeviceClass(Enum):
    """ 任务状态枚举类 """

    KEYPAD = 'Keypad'  # 数字键盘
    MAGNET_IC = 'MagnetIC'  # 磁条读写器
    FINGER = 'FingerScanner'  # 指纹仪
    PBOCICCard = 'PBOCICCard'  # IC卡
    ID_CARD = 'IDCard'  # 身份证识别器
    QR_CODE = 'QRCode'  # 二维码扫描仪
    PRINTER = 'Printer'  # 针式打印机
    LASER_PRINTER = 'LaserPrinter'  # 激光打印机
    JOURNAL_PRINTER = 'JournalPrinter'  # 流水打印机
    EVALUATOR = 'Evaluator'  # 评价器
    MULTI_FUNC_SCREEN = 'MultiFuncScreen'  # 多功能屏幕
    SHARED_DEVICE_CLIENT = 'SharedDeviceClient'  # 共享外设客户端

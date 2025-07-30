# author: haoliqing
# date: 2023/9/6 17:58
# desc:
import json
from abc import ABCMeta, abstractmethod
from device.base_device import Device
from enum import Enum, unique
from typing import List


class TranInfo(object):
    """生成ARQC时使用的交易数据"""

    def __init__(self):
        self.tran_ccy: str = None
        """交易货币类型"""

        self.tran_amt: str = None
        """交易金额 不带小数点,单位为分,"""

        self.tran_type: str = None
        """交易类型"""

        self.org_name: str = None
        """商户名称"""

        self.inputAid: str = None
        """卡应用标识"""

        self.tran_date: str = None
        """交易日期"""

        self.tran_time: str = None
        """交易时间"""

    def __str__(self):
        # return json.dumps(self.__dict__, ensure_ascii=False)
        return self.__dict__


class DetailInfo(object):
    """从IC卡中读取的交易日志内容"""

    def __init__(self):
        self.ccy: str = None
        """交易货币代码"""

        self.auth_amt: str = None
        """授权金额"""

        self.other_amt: str = None
        """其他金额"""

        self.tran_date: str = None
        """交易日期"""

        self.tran_time: str = None
        """交易时间"""

        self.tran_type: str = None
        """交易类型"""

        self.org_name: str = None
        """商户名称"""

        self.country: str = None
        """终端国家代码"""

        self.counter_app: str = None
        """应用交易计数器"""


class CreditInfo(object):
    """从IC卡中读取的圈存明细信息"""

    def __init__(self):
        self.before_amt: str = None
        """圈存前金额"""

        self.after_amt: str = None
        """圈存后金额"""

        self.tran_date: str = None
        """交易日期"""

        self.tran_time: str = None
        """交易时间"""

        self.org_name: str = None
        """商户名称"""

        self.country: str = None
        """终端国家代码"""

        self.counter_app: str = None
        """应用交易计数器"""


@unique
class PBOCVersion(Enum):
    """ IC卡卡片类型,根据PBOC版本区分为是2.0的卡还是3.0的卡 """
    PBOC_VER_20 = 2  # PBOC 2.0
    PBOC_VER_30 = 3  # PBOC 3.0
    PBOC_VER_UNKNOWN = 0  # 未知


@unique
class ContactMode(Enum):
    """ 当前IC卡卡片操作使用的接触方式, PBOC卡片接触方式：接触式或者非接触式。 """
    CONTACT = 1  # 接触式
    CONTACTLESS = 2  # 非接触式
    AUTOMATIC = 3  # 自动
    UNKNOWN = 0  # 未知


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        return super().default(obj)


class FinanceICInfo(object):
    """金融IC卡信息"""

    def __init__(self):
        self.err_code: int = 0
        """错误码，该值不会返回给交易，仅用于标识读卡是否成功，小于0则表示失败，否则为成功，默认为0"""

        self.arqc: str = None
        """读取到的原始arqc，格式：3位arqc长度+arqc内容"""

        self.cert_type: str = None
        """证件类型"""

        self.cert_no: str = None
        """证件号"""

        self.card_no: str = None
        """卡号"""

        self.card_serial_no: str = None
        """卡序号"""

        self.owner_name: str = None
        """持卡人姓名"""

        self.balance: str = None
        """电子现金余额"""

        self.ccy: str = None
        """币种"""

        self.tran_detail: List[DetailInfo] = None
        """交易日志信息"""

        self.credit_detail: List[CreditInfo] = None
        """圈存明细信息"""

        self.issue_branch_data: str = None
        """发卡行应用数据"""

        self.aid: str = "A000000333010101"
        """应用标识,有的驱动中获取不到，给定A000000333010101"""

        self.arqc_source: str = None
        """
        ARQC源数据,该值符合PBOC 2.0规范
        具体内容为
        授权金额（12位）+其它金额（12位）+终端国家代码（4位）+终端验证结果（10位）+交易货币代码（4位）
        +交易日期（6位）+交易类型（2位）+不可预知数（8位）+应用交互特征（AIP）（4位）
        +应用交易计数器（ATC）（4位）+卡片验证结果（CVR）（8位）
        """

        self.tran_counter: str = None
        """应用交易计数器"""

        self.balance_limit: str = None
        """余额上限"""

        self.single_limit: str = None
        """单笔金额上限"""

        self.verify_result: str = None
        """终端验证结果"""

        self.arqc_only: str = None
        """6位arqc数据，arqc密文，16位，符合PBOC规范"""

        self.effective_date: str = None
        """应用生效日期"""

        self.overdue_date: str = None
        """应用失效日期"""

        self.track2Data: str = None
        """二磁道等效数据"""

        self.pboc_ver: PBOCVersion = PBOCVersion.PBOC_VER_UNKNOWN
        """卡支持的PBOC版本 ： 2.0 或者 3.0"""

        self.contact_mode: ContactMode = ContactMode.UNKNOWN
        """当前IC卡卡片操作使用的接触方式"""

    def __str__(self):
        # return (
        #     f'FinanceICInfo("arqc":\"{self.arqc}\","cert_type":\"{self.cert_type}\","cert_no":\"{self.cert_no}\",'
        #     f'"card_no":\"{self.card_no}\",'
        #     f'"card_serial_no":\"{self.card_serial_no}\","owner_name":\"{self.owner_name}\","balance":\"{self.balance}\",'
        #     f'"ccy":\"{self.ccy}\","tran_detail":{self.tran_detail},"issue_branch_data":\"{self.issue_branch_data}\",'
        #     f'"aid":\"{self.aid}\","arqc_source":\"{self.arqc_source}\",'
        #     f'"tran_counter":\"{self.tran_counter}\","balance_limit":\"{self.balance_limit}\","single_limit":\"{self.single_limit}\",'
        #     f'"verify_result":\"{self.verify_result}\","arqc_only":\"{self.arqc_only}\","effective_date":\"{self.effective_date}\",'
        #     f'"overdue_date":\"{self.overdue_date}\","track2Data":\"{self.track2Data}\","pboc_ver":\"{self.pboc_ver}\",'
        #     f'"contact_mode":\"{self.contact_mode}\")')
        # return self.__dict__
        return json.dumps(self.__dict__, ensure_ascii=False, cls=CustomJSONEncoder)


class WriteICResult(object):
    """写入金融IC卡返回结果"""

    def __init__(self):
        self.err_code: int = 0
        """错误码，该值不会返回给交易，仅用于标识读卡是否成功，小于0则表示失败，否则为成功，默认为0"""

        self.script_result: str = None
        """脚本执行结果"""

        self.tc: str = None
        """GAC2的返回结果,一般与ARQC一致"""


class FinanceICCardRWer(Device, metaclass=ABCMeta):
    """金融IC卡读写驱动适配器基类"""

    @abstractmethod
    def power_on(self) -> int:
        """
        IC卡上电
        :return: 执行结果，小于0为失败，否则为成功
        """
        pass

    @abstractmethod
    def power_off(self) -> int:
        """
        IC卡下电
        :return:  执行结果，小于0为失败，否则为成功
        """
        pass

    @abstractmethod
    def read_finance_ic_info(self, tran_info: TranInfo) -> FinanceICInfo:
        """
        获取金融IC卡信息，读取的信息包括：卡基本信息，arqc，交易详细信息
        :param tran_info: 交易信息
        :return:　读取到的卡信息，若返回值为None，则获取失败，否则读卡的成功与失败由FinanceICInfo.errorCode来决定，
        若该值小于0，则认为读卡失败，否则为读卡成功，该值需要在驱动实现中自行设置，默认为0
        """
        pass

    def write_finance_ic_info(self, data: str) -> WriteICResult:
        """
        写入金融IC卡信息
        :param data:　写入的数据
            写IC卡时，写入卡中的数据符合PBOC2.0规范的55域数据
            一般格式为"910A + 16位的ARPC + 3030 + 写卡脚本”
            写卡脚本格式为71(72)xx xx xx xx
        :return:　写卡的返回结果，若返回值为None，则获取失败，否则写卡的成功与失败由WriteICResult.errorCode来决定，
        若该值小于0，则认为写卡失败，否则为写卡成功，该值需要在驱动实现中自行设置，默认为0
        """

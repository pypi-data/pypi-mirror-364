# author: haoliqing
# date: 2023/9/14 16:56
# desc:
import asyncio
import base64
import datetime
import os
import sys
import time
import traceback

from common import global_constants
from logger.device_logger import logger

path: str = os.path.dirname(os.path.abspath(__file__))
path = path.replace("common", "")


def read_file(file_path: str) -> str:
    """根据文件路径读取文件并返回文件内容"""
    file_data = None
    try:
        with open(file_path, 'rt', encoding='utf-8') as file_data:
            return file_data.read()
    except FileNotFoundError:
        logger.error('读取文件[{0}]时发生异常：无法打开指定的文件!'.format(file_path))
    except LookupError:
        logger.error('读取文件[{0}]时发生异常：指定了未知的编码!'.format(file_path))
    except UnicodeDecodeError:
        logger.error('读取文件[{0}]时发生异常：读取文件时解码错误!'.format(file_path))


def get_absolute_path(relative_path: str) -> str:
    """
    获取工程内文件的绝对路径
    :param relative_path: 工程内文件相对路径
    :return:
    """
    return os.path.join(path, "./" + relative_path)


def create_obj_by_cls_path(cls_path: str, *args):
    """
    根据全类名创建对象
    :param cls_path: 类文件名+类名全路径，如task.impl.general_device_task.GeneralDeviceTask
    :return: 创建的对象
    """
    index = cls_path.rfind('.')
    module_name = cls_path[:index]
    cls_name = cls_path[index + 1:]
    __import__(module_name)
    mod = sys.modules[module_name]
    aclass = getattr(mod, cls_name)
    return aclass(*args)


def send_socket_msg(socket, msg: str) -> bool:
    """
    发送socket消息
    :param socket:
    :param msg: 消息内容
    :param is_async: 是否异步发送，若在外设调用主线程中调用该方法，该值为True，在子线程中调用，该值为False，默认为False,
            若该值输入错误，发送消息时会抛出异常
    :return: 是否发送成功
    """
    try:
        if socket:
            logger.info("向客户端返回信息：{0}".format(msg))
            try:
                asyncio.run(socket.send(msg))
            except RuntimeError:
                loop = asyncio.get_event_loop()
                loop.create_task(socket.send(msg))
            return True
        else:
            logger.error("socket对象为空，无法发送消息")
            return False
    except Exception as e:
        logger.error("发送socket消息时发生异常: {0}, 异常信息：{1}".format(str(e), traceback.format_exc()))
        return False


def image_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return global_constants.BASE64_PREFIX + encoded_string.decode('utf-8')


def get_save_pdir() -> str:
    """
    保存
    @return: 用户目录/deviceTemp/当前日期8位数字
    """
    home_dir = os.path.expanduser("~")
    separator = os.path.sep
    today_str = str(datetime.date.today()).replace("-", "")
    device_path = os.path.join(home_dir, "deviceTemp", today_str)
    if not os.path.exists(device_path):
        os.makedirs(device_path)
    return device_path + separator


def get_save_pdir_linux() -> str:
    # 定义要创建的目录路径
    today_str = str(datetime.date.today()).replace("-", "")
    new_dir = "/tmp/deviceTemp/" + today_str
    # 使用 os.makedirs() 创建多级目录
    os.makedirs(new_dir, exist_ok=True)
    return new_dir + os.path.sep


def get_time_stamp():
    return (str(time.time())).replace(".", "")


if __name__ == "__main__":
    # obj = create_obj_by_cls_path("task.impl.general_device_task.GeneralDeviceTask", 111)
    # base_ = image_to_base64("D:\\Image\\622827200003083719-head.bmp.png")
    # print(base_)
    user_dir = get_save_pdir()
    print(user_dir)

# author: haoliqing
# date: 2023/10/16 20:02
# desc:
import configparser
import datetime
import logging
import os
cur_path = os.path.abspath('.') + '/logs'
if not os.path.exists(cur_path):
    os.makedirs(cur_path)  # 目录不存在则创建
log_file = '%s/sys_%s.log' % (cur_path, datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d'))
# level：设置日志输出的最低级别，即低于此级别的日志都不会输出
# 在平时开发测试的时候能够设置成logging.debug以便定位问题，但正式上线后建议设置为logging.WARNING，既能够下降系统I/O的负荷，也能够避免输出过多的无用日志信息
conf = configparser.ConfigParser()  # 类的实例化

curpath: str = os.path.dirname(os.path.realpath(__file__))
curpath = curpath.replace("logger", "")
path = os.path.join(curpath, './config/device_service.ini')
conf.read(path, encoding='utf-8')

log_level = logging.getLevelName(conf.get("log", 'root_level', fallback='INFO'))
# format：设置日志的字符串输出格式
log_format = '%(asctime)s - %(pathname)s.%(funcName)s - %(lineno)d [%(levelname)s]: %(message)s'
logger = logging.getLogger()
# 全局日志级别
logger.setLevel(log_level)

log_formatter = logging.Formatter(log_format)

file_handler = logging.FileHandler(log_file)
# 设置此Handler的最低日志级别
file_handler.setLevel(logging.getLevelName(conf.get("log", 'file_level', fallback='INFO')))
# 设置此Handler的日志输出字符串格式
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# 建立一个StreamHandler，将日志输出到Stream，默认输出到sys.stderr
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.getLevelName(conf.get("log", 'console_level', fallback='INFO')))
stream_handler.setFormatter(log_formatter)
# 将不一样的Handler添加到logger中，日志就会同时输出到不一样的Handler控制的输出中
# 注意若是此logger在以前使用basicConfig进行基础配置，由于basicConfig会自动建立一个Handler，因此此logger将会有3个Handler
# 会将日志同时输出到3个Handler控制的输出中
logger.addHandler(stream_handler)

"""
# 如下日志输出因为level被设置为了logging.WARNING，因此debug和info的日志不会被输出
logger.debug('This is a debug message!')
logger.info('This is a info message!')
logger.warning('This is a warning message!')
logger.error('This is a error message!')
logger.critical('This is a critical message!')
"""

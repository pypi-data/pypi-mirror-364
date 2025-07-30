# author: haoliqing
# date: 2023/8/16 14:30
# desc: 单例类型装饰器
def Singleton(cls):
    instance = {}

    def _singleton_wrapper(*args, **kargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kargs)
        return instance[cls]

    return _singleton_wrapper

from setuptools import find_packages, setup

setup(
    name='driverApi',  # 与要打包的报名要一致
    version='1.0.7',  # 每次发布pypi的版本号不可重复
    packages=find_packages(include=['device', 'device.*', 'driver', 'driver.*', 'logger'],
                           exclude=['driver.cache', 'driver.cache.*', 'driver.impl', 'driver.impl.*',
                                    'driver.factory', 'driver.factory.*']),  # 指定要依赖的包和排除的包
    py_modules=['common.singleton', 'common.global_constants', 'common.common_utils'],
    install_requires=[],  # 项目依赖哪些库，这些库会在pip install的时候自动安装
    author='NanYuan',
    author_email='28766392428@qq.com',
    description='外设驱动接口',  # 项目的简短描述
    long_description=open('device_service插件指南.md', encoding='utf-8').read(),  # 项目的详细描述
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent"
    ],
)

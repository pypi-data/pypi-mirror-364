# -*- coding: utf-8 -*-

import shutil

import setuptools
from setuptools.command.install_scripts import install_scripts

from lesscode.version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="lesscode-py",
    version=__version__,
    author="Chao.yy",
    author_email="yuyc@ishangqi.com",
    description="lesscode-python 是基于tornado的web开发脚手架项目，该项目初衷为简化开发过程，让研发人员更加关注业务。",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/yongchao9/lesscode-python",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        # "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    platforms='python',
    install_requires=[
        # "tornado==6.0",
        # "tornado-sqlalchemy==0.7.0",
        # "aiomysql==0.0.22",
        # "motor==2.5.1",
        # "elasticsearch==7.15.2",
        # "aiopg==1.3.3",
        # "aiohttp==3.8.3",
        # "crypto==1.4.1",
        # "pycryptodome==3.12.0",
        # "aioredis==2.0.1",
        # "DBUtils==3.0.2",
        # "redis==4.1.4",
        # "requests==2.27.1",
        # "neo4j==5.0.0",
        # "snowland-smx==0.3.1",
        # "py_eureka_client==0.11.3",
        # "ks3sdk==1.5.0",
        # "filechunkio==1.8",
        # "APScheduler==3.9.1",
        # "nacos-sdk-python==0.1.8",
        # "pika==1.3.0",
        # "kafka-python==2.0.2",
        # "nebula3-python==3.4.0"
    ]

)
"""
        "aiopg>=1.3.3",
"""
"""
1、打包流程
打包过程中也可以多增加一些额外的操作，减少上传中的错误

# 先升级打包工具
pip install --upgrade setuptools wheel twine

# 打包
python setup.py sdist bdist_wheel

# 检查
twine check dist/*

# 上传pypi
twine upload dist/*
twine upload dist/* -u yuyc -p yu230225
twine upload dist/* --repository-url https://pypi.chanyeos.com/ -u admin -p shangqi
# 安装最新的版本测试
pip install -U lesscode-py -i https://pypi.org/simple
pip install -U lesscode-py -i https://pypi.chanyeos.com/simple
"""

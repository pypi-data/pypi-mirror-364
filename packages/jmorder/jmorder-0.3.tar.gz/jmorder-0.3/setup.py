from setuptools import setup

setup(
    name="jmorder",
    version="0.3",
    packages=["jmorder"],  # 指定包含的模块
    install_requires=[
        "pandas",
        "xlrd>=1.2.0",  # 自动安装 xlrd
        # 其他依赖...
    ],
)
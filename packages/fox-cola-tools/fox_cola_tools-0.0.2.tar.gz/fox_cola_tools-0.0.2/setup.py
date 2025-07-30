# setup.py

from setuptools import setup, find_packages

setup(
    name="fox-cola-tools",  # 上传到 PyPI 的包名
    version="0.0.2",
    description="fox-cola-tools",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Sun Jia Peng",
    author_email="zybancao@gmail.com",
    url="https://github.com/Joker-Pro-Max/fox-cola-tools",
    packages=find_packages(),  # 自动查找所有模块
    license="MIT",  # ✅ 建议保留
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

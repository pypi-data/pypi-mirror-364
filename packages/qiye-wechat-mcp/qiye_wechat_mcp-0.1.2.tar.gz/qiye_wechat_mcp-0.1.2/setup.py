#!/usr/bin/env python3
"""企业微信消息 MCP 服务器安装脚本"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="qiye-wechat-mcp",
    version="0.1.2",
    author="shellus",
    author_email="353358601@qq.com",
    description="企业微信群机器人 MCP 服务器",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shellus/qiye_wechat_mcp.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "requests>=2.25.0",
        "python-dotenv>=0.19.0",
    ],
    entry_points={
        "console_scripts": [
            "qiye-wechat-mcp=qiye_wechat_mcp.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)

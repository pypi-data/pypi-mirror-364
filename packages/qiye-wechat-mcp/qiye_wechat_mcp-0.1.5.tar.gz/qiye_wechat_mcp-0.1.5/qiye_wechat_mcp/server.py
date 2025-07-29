#!/usr/bin/env python3
"""企业微信群机器人 MCP 服务器 - 超简化版本"""

import os
import requests
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# 加载环境变量
load_dotenv()

# 获取配置
WEBHOOK_URL = os.getenv('WECHAT_WEBHOOK_URL', '')
if not WEBHOOK_URL or 'webhook/send' not in WEBHOOK_URL:
    raise ValueError("请设置正确的 WECHAT_WEBHOOK_URL")

# 创建MCP服务器
mcp = FastMCP("企业微信消息")

@mcp.tool()
def send_text_message(content: str) -> str:
    """发送文本消息到企业微信群"""
    payload = {"msgtype": "text", "text": {"content": content}}
    response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
    result = response.json()
    return "✅ 发送成功" if result.get('errcode', 0) == 0 else f"❌ 发送失败: {result.get('errmsg', '未知错误')}"

@mcp.tool()
def send_markdown_message(content: str) -> str:
    """发送Markdown消息到企业微信群"""
    payload = {"msgtype": "markdown", "markdown": {"content": content}}
    response = requests.post(WEBHOOK_URL, json=payload, timeout=10)
    result = response.json()
    return "✅ 发送成功" if result.get('errcode', 0) == 0 else f"❌ 发送失败: {result.get('errmsg', '未知错误')}"

def main():
    """主入口函数，供pip安装后的命令行调用"""
    mcp.run()

if __name__ == "__main__":
    main()



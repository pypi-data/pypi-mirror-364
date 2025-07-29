"""测试MCP服务器"""

import os
import pytest
from unittest.mock import patch, MagicMock
from qiye_wechat_mcp.server import QiyeWeChatMCPServer


class TestQiyeWeChatMCPServer:
    """测试企业微信MCP服务器"""
    
    def test_init_without_webhook_url(self):
        """测试没有Webhook URL时的初始化"""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(ValueError, match="缺少必要的企业微信配置"):
                QiyeWeChatMCPServer()
    
    def test_init_with_invalid_webhook_url(self):
        """测试无效Webhook URL时的初始化"""
        with patch.dict(os.environ, {'WECHAT_WEBHOOK_URL': 'https://invalid.url'}, clear=True):
            with pytest.raises(ValueError, match="WECHAT_WEBHOOK_URL 格式不正确"):
                QiyeWeChatMCPServer()
    
    def test_init_with_valid_webhook_url(self):
        """测试有效Webhook URL时的初始化"""
        webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key"
        with patch.dict(os.environ, {'WECHAT_WEBHOOK_URL': webhook_url}, clear=True):
            server = QiyeWeChatMCPServer()
            assert server.webhook_url == webhook_url
            assert len(server.message_history) == 0
    
    @pytest.mark.asyncio
    async def test_send_text_message_empty_content(self):
        """测试发送空文本消息"""
        webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key"
        with patch.dict(os.environ, {'WECHAT_WEBHOOK_URL': webhook_url}, clear=True):
            server = QiyeWeChatMCPServer()

            # 空内容应该抛出异常
            with pytest.raises(ValueError, match="消息内容不能为空"):
                await server._send_text_message("")
    
    @pytest.mark.asyncio
    async def test_send_text_message_success(self):
        """测试成功发送文本消息"""
        webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key"
        with patch.dict(os.environ, {'WECHAT_WEBHOOK_URL': webhook_url}, clear=True):
            server = QiyeWeChatMCPServer()
            
            # Mock HTTP响应
            mock_response = MagicMock()
            mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
            mock_response.raise_for_status.return_value = None
            
            with patch.object(server.session, 'post', return_value=mock_response):
                result = await server._send_text_message("Hello World")
                
                assert len(result) == 1
                assert "发送成功" in result[0].text
                assert len(server.message_history) == 1
    
    @pytest.mark.asyncio
    async def test_send_markdown_message_success(self):
        """测试成功发送Markdown消息"""
        webhook_url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=test-key"
        with patch.dict(os.environ, {'WECHAT_WEBHOOK_URL': webhook_url}, clear=True):
            server = QiyeWeChatMCPServer()
            
            # Mock HTTP响应
            mock_response = MagicMock()
            mock_response.json.return_value = {"errcode": 0, "errmsg": "ok"}
            mock_response.raise_for_status.return_value = None
            
            markdown_content = "## 测试\n这是一个**测试**消息"
            
            with patch.object(server.session, 'post', return_value=mock_response):
                result = await server._send_markdown_message(markdown_content)
                
                assert len(result) == 1
                assert "发送成功" in result[0].text
                assert len(server.message_history) == 1

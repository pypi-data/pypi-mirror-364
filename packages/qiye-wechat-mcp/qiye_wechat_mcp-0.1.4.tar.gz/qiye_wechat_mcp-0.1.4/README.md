# 企业微信消息 MCP 服务器

简单的企业微信群机器人 MCP 服务器，让 AI 助手能发送消息到企业微信群。

## 安装

```bash
uvx install qiye-wechat-mcp
```

## 快速开始

### 1. 配置企业微信群机器人
1. 在企业微信群中添加群机器人
2. 复制机器人的 Webhook URL

### 4. 配置 mcpServers
```json
{
  "mcpServers": {
    "企业微信": {
      "command": "uvx",
      "args": ["qiye-wechat-mcp@latest"],
      "env": {
        "WECHAT_WEBHOOK_URL": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=your-webhook-key"
      }
    }
  }
}
```

## 功能
- `send_text_message(content)` - 发送文本消息
- `send_markdown_message(content)` - 发送Markdown消息

## AI提示词
```markdown
1. 使用中文回复
2. 在完成任务得最后，使用`qiye_wechat_mcp.send_text_message(content)`发送完成通知。
```
---


就这么简单！

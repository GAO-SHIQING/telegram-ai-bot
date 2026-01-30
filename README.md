# Telegram AI 机器人

<div align="center">

🤖 功能丰富的 Telegram AI 聊天机器人

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)

[功能特点](#-特点) • [快速开始](#-快速开始) • [文档](#-文档) • [贡献](#-贡献)

</div>

---

基于 python-telegram-bot + AI 的智能对话机器人，支持自然对话和上下文记忆。

## ✨ 特点

- 🤖 **官方 API** - 使用 Telegram Bot API，稳定可靠
- 🎭 **多种人设** - 5种风格：小高同学、丰子、小助手、逗比、学霸
- 🖼️ **图片识别** - 发送图片即可识别内容
- 🎤 **语音识别** - 发送语音自动转文字并回复
- 🔍 **联网搜索** - 获取实时信息和知识
- 🧠 **记忆系统** - 记住你的重要信息，个性化对话
- 💬 **自然对话** - 像朋友一样聊天
- 📊 **使用统计** - 记录你的聊天习惯和偏好
- 👥 **群聊支持** - @ 机器人即可在群里对话
- 🔄 **上下文理解** - 记住对话历史，支持连续对话
- 🚀 **快速响应** - 实时接收和回复消息
- 🛡️ **健壮可靠** - 多层重试机制，确保消息不遗漏
- 🌐 **跨平台** - 支持 Windows、Linux、macOS

## 📋 前置要求

- Python 3.11+
- Telegram 账号
- AI API 密钥（OpenAI、DeepSeek、SiliconFlow 等）

## 🚀 快速开始

### 1. 创建 Telegram Bot

1. 在 Telegram 中找到 [@BotFather](https://t.me/botfather)
2. 发送 `/newbot` 创建新机器人
3. 按提示设置机器人名称和用户名
4. 获取 Bot Token（格式：`123456789:ABCdefGHIjklMNOpqrsTUVwxyz`）

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env`，填写配置：

```env
# Telegram 配置
TELEGRAM_BOT_TOKEN=你的_Bot_Token

# AI 配置
OPENAI_API_KEY=你的API密钥
OPENAI_BASE_URL=https://api.siliconflow.cn/v1
MODEL_NAME=deepseek-ai/DeepSeek-V3

# 机器人配置
BOT_NAME=小高同学
```

**常用 AI API 配置：**
- SiliconFlow: `https://api.siliconflow.cn/v1`
- DeepSeek: `https://api.deepseek.com/v1`
- OpenAI: `https://api.openai.com/v1`

### 4. 启动机器人

```bash
python telegram_bot.py
```

### 5. 使用说明

1. 在 Telegram 中搜索你的机器人用户名
2. 点击 "Start" 或发送 `/start`
3. 开始聊天！

## 💡 工作原理

```
Telegram API 接收消息 → AI 生成回复 → Telegram API 发送回复
```

## 🎮 可用命令

- `/start` - 显示欢迎信息
- `/help` - 显示帮助信息
- `/persona` - 查看当前人设和可选列表
- `/persona 小高` - 切换到小高同学
- `/persona 丰子` - 切换到丰子
- `/persona 小助手` - 切换到小助手
- `/persona 逗比` - 切换到逗比
- `/persona 学霸` - 切换到学霸
- `/stats` - 查看使用统计
- `/memory` - 查看记住的信息
- `/memory 名字 小明` - 记住信息
- `/forget 名字` - 忘记信息
- `/search Python教程` - 联网搜索
- `/clear` - 清空对话历史

## 🎭 人设系统

机器人支持多种人设，每个用户可以独立选择：

### 小高同学
- 随意自然的男生
- 像朋友一样聊天
- 语气轻松随意

### 丰子
- 温柔体贴的女生
- 聊天温和自然
- 语气温柔但不夸张

### 小助手
- 专业高效的AI助理
- 帮你解决问题
- 回复准确有条理

### 逗比
- 幽默搞笑
- 聊天轻松愉快
- 让你开心

### 学霸
- 知识渊博
- 严谨专业
- 擅长解答问题

**切换方法：**
```
/persona          # 查看当前人设
/persona 小高     # 切换到小高同学
/persona 丰子     # 切换到丰子
/persona 小助手   # 切换到小助手
/persona 逗比     # 切换到逗比
/persona 学霸     # 切换到学霸
```

## 📊 使用统计

使用 `/stats` 命令查看你的使用统计：
- 总消息数和对话次数
- 使用天数和日均消息
- 最常用的人设
- 每个人设的使用次数
- 首次和最近使用时间

## 👥 群聊使用

将机器人添加到群组后：
1. @ 机器人发送消息：`@你的机器人 你好`
2. 或回复机器人的消息
3. 机器人会自动回复

私聊时无需 @，直接发送消息即可。

## 🖼️ 图片识别

发送图片给机器人，它会自动识别并描述图片内容：
- 直接发送图片
- 或添加说明文字：`这是什么？`
- 支持图片问答

**注意：** 需要使用支持视觉的 AI 模型（如 GPT-4V、DeepSeek-VL 等）

## 🧠 记忆系统

机器人可以记住你的重要信息：

**添加记忆：**
```
/memory 名字 小明
/memory 爱好 编程
/memory 生日 1月1日
```

**查看记忆：**
```
/memory
```

**删除记忆：**
```
/forget 名字
```

机器人会在对话中自动使用这些记忆，让聊天更个性化。

## 🎤 语音识别

发送语音消息，机器人会自动：
1. 将语音转为文字
2. 理解你的问题
3. 用文字回复

**注意：** 需要 OpenAI Whisper API 支持

## 🔍 联网搜索

使用 `/search` 命令获取实时信息：

```
/search Python教程
/search 今天天气
/search 最新新闻
```

机器人会搜索网络并返回相关结果。

## ⚙️ 配置说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot Token | - |
| `BOT_NAME` | 机器人名称 | 小高同学 |
| `OPENAI_API_KEY` | AI API 密钥 | - |
| `OPENAI_BASE_URL` | AI API 地址 | - |
| `MODEL_NAME` | AI 模型名称 | - |
| `MAX_API_RETRY` | API 重试次数 | 3 |

## 📁 项目结构

```
telegram-ai-bot/
├── telegram_bot.py       # 主程序
├── ai_client.py          # AI 客户端
├── config.py             # 配置管理
├── test_config.py        # 配置测试脚本
├── .env                  # 环境变量（需自己创建）
├── .env.example          # 环境变量示例
├── requirements.txt      # 依赖列表
├── start.bat             # Windows 启动脚本
├── README.md             # 项目说明
├── QUICKSTART.md         # 快速开始指南
├── MIGRATION.md          # 迁移指南
├── DEPLOY.md             # 部署指南
└── chat_history/         # 对话历史（自动生成）
```

## 🔧 常见问题

### Q: 如何获取 Bot Token？

**A:** 
1. 在 Telegram 中找到 [@BotFather](https://t.me/botfather)
2. 发送 `/newbot` 并按提示操作
3. 创建成功后会收到 Token

### Q: 机器人不回复消息？

**A:** 检查以下几点：
1. Bot Token 是否正确
2. AI API 配置是否正确
3. 查看终端日志输出
4. 确认机器人已启动

### Q: 如何修改机器人人设？

**A:** 修改 `config.py` 中的 `SYSTEM_PROMPT`，调整"小高同学"的人设和回复风格。

### Q: 支持群聊吗？

**A:** 支持！将机器人添加到群组即可。如需只在被 @ 时回复，可以修改代码添加过滤条件。

### Q: 如何部署到服务器？

**A:** 
1. 将代码上传到服务器
2. 安装依赖：`pip install -r requirements.txt`
3. 配置 `.env` 文件
4. 使用 `nohup` 或 `systemd` 后台运行：
   ```bash
   nohup python telegram_bot.py > bot.log 2>&1 &
   ```

## 🎯 技术特点

### 消息处理
- 使用 Telegram Bot API 接收消息
- 异步处理，支持高并发
- 自动显示"正在输入"状态

### 对话管理
- 每个用户独立的对话历史
- 自动保存和加载历史记录
- 支持清空历史重新开始

### 回复优化
- 支持分条发送（用 `|||` 分隔）
- 自动清理机器人用语
- 确保回复自然流畅

### 错误处理
- API 调用失败自动重试
- 异常捕获和日志记录
- 用户友好的错误提示

## 📝 更新日志

### v2.0.0 (2026-01-29)
- ✅ 从微信机器人重塑为 Telegram 机器人
- ✅ 使用官方 Telegram Bot API
- ✅ 简化架构，去除 OCR 依赖
- ✅ 保留 AI 对话和历史记录功能
- ✅ 支持跨平台运行
- ✅ 异步处理，性能更优

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**注意：** 请遵守 Telegram Bot API 使用条款，不要用于垃圾信息或骚扰用户。


## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

查看 [贡献指南](CONTRIBUTING.md) 了解更多。

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

## ⭐ Star History

如果这个项目对你有帮助，请给个 Star ⭐

## 🔗 相关链接

- [Telegram Bot API 文档](https://core.telegram.org/bots/api)
- [python-telegram-bot 文档](https://docs.python-telegram-bot.org/)
- [OpenAI API 文档](https://platform.openai.com/docs)

---

<div align="center">
Made with ❤️ by Telegram AI Bot Contributors
</div>

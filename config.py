import os
from dotenv import load_dotenv

load_dotenv()

# ========== Telegram 配置 ==========
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# ========== AI 聊天配置 ==========
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")

# ========== 机器人配置 ==========
BOT_NAME = os.getenv("BOT_NAME", "AI 助手")

# 代理配置（如果需要）
PROXY_URL = os.getenv("PROXY_URL", "")

# API 重试次数
MAX_API_RETRY = int(os.getenv("MAX_API_RETRY", "3"))

# 历史记录目录
HISTORY_DIR = os.getenv("HISTORY_DIR", "chat_history")

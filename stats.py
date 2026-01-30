"""
用户统计模块
记录和查询用户使用统计数据
"""
import json
from pathlib import Path
from datetime import datetime
from collections import Counter
from loguru import logger


class StatsManager:
    """统计管理器"""
    
    def __init__(self, stats_dir="chat_history"):
        self.stats_dir = Path(stats_dir)
        self.stats_dir.mkdir(exist_ok=True)
        self.stats_file = self.stats_dir / "user_stats.json"
        self.stats = self._load_stats()
    
    def _load_stats(self) -> dict:
        """加载统计数据"""
        if self.stats_file.exists():
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载统计数据失败: {e}")
                return {}
        return {}
    
    def _save_stats(self):
        """保存统计数据"""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存统计数据失败: {e}")
    
    def _init_user_stats(self, user_id: str):
        """初始化用户统计"""
        if user_id not in self.stats:
            self.stats[user_id] = {
                "total_messages": 0,
                "total_conversations": 0,
                "first_use": datetime.now().isoformat(),
                "last_use": datetime.now().isoformat(),
                "persona_usage": {},
                "daily_messages": {}
            }
    
    def record_message(self, user_id: str, persona_key: str):
        """记录一次消息"""
        self._init_user_stats(user_id)
        
        user_stats = self.stats[user_id]
        user_stats["total_messages"] += 1
        user_stats["last_use"] = datetime.now().isoformat()
        
        # 记录人设使用
        if persona_key not in user_stats["persona_usage"]:
            user_stats["persona_usage"][persona_key] = 0
        user_stats["persona_usage"][persona_key] += 1
        
        # 记录每日消息数
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in user_stats["daily_messages"]:
            user_stats["daily_messages"][today] = 0
        user_stats["daily_messages"][today] += 1
        
        self._save_stats()
    
    def record_conversation(self, user_id: str):
        """记录一次对话（首次消息）"""
        self._init_user_stats(user_id)
        self.stats[user_id]["total_conversations"] += 1
        self._save_stats()
    
    def get_user_stats(self, user_id: str) -> dict:
        """获取用户统计"""
        if user_id not in self.stats:
            return None
        
        user_stats = self.stats[user_id]
        
        # 计算使用天数
        first_use = datetime.fromisoformat(user_stats["first_use"])
        days_used = (datetime.now() - first_use).days + 1
        
        # 找出最常用的人设
        persona_usage = user_stats.get("persona_usage", {})
        favorite_persona = max(persona_usage.items(), key=lambda x: x[1])[0] if persona_usage else "未知"
        
        # 计算平均每天消息数
        avg_daily = user_stats["total_messages"] / days_used if days_used > 0 else 0
        
        return {
            "total_messages": user_stats["total_messages"],
            "total_conversations": user_stats["total_conversations"],
            "days_used": days_used,
            "first_use": first_use.strftime("%Y-%m-%d"),
            "last_use": datetime.fromisoformat(user_stats["last_use"]).strftime("%Y-%m-%d"),
            "favorite_persona": favorite_persona,
            "persona_usage": persona_usage,
            "avg_daily_messages": round(avg_daily, 1)
        }
    
    def format_stats(self, user_id: str) -> str:
        """格式化统计信息为文本"""
        stats = self.get_user_stats(user_id)
        
        if not stats:
            return "📊 还没有统计数据哦，快来聊天吧！"
        
        # 格式化人设使用情况
        persona_lines = []
        for persona, count in sorted(stats["persona_usage"].items(), key=lambda x: x[1], reverse=True):
            persona_lines.append(f"  • {persona}: {count}次")
        persona_text = "\n".join(persona_lines) if persona_lines else "  暂无数据"
        
        text = (
            f"📊 你的使用统计\n\n"
            f"💬 总消息数: {stats['total_messages']}\n"
            f"🔄 对话次数: {stats['total_conversations']}\n"
            f"📅 使用天数: {stats['days_used']}天\n"
            f"📈 日均消息: {stats['avg_daily_messages']}条\n"
            f"⭐ 最爱人设: {stats['favorite_persona']}\n\n"
            f"🎭 人设使用情况:\n{persona_text}\n\n"
            f"🕐 首次使用: {stats['first_use']}\n"
            f"🕐 最近使用: {stats['last_use']}"
        )
        
        return text

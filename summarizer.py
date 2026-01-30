"""
群消息总结模块
分析群消息并生成总结
"""
from datetime import datetime
from collections import Counter
from loguru import logger


class MessageSummarizer:
    """消息总结器"""
    
    def __init__(self, ai_client):
        self.ai = ai_client
    
    def generate_summary(self, chat_id: int, messages: list, chat_title: str = "群聊") -> str:
        """生成群消息总结"""
        if not messages:
            return "📊 暂无消息可总结"
        
        # 基础统计
        stats = self._calculate_stats(messages)
        
        # 提取消息内容用于AI总结
        message_text = self._format_messages_for_ai(messages)
        
        # 调用AI生成总结
        ai_summary = self._generate_ai_summary(message_text, stats)
        
        # 格式化最终总结
        final_summary = self._format_final_summary(
            chat_title=chat_title,
            stats=stats,
            ai_summary=ai_summary
        )
        
        return final_summary
    
    def _calculate_stats(self, messages: list) -> dict:
        """计算统计信息"""
        # 用户消息数统计
        user_counts = Counter()
        for msg in messages:
            user_counts[msg["username"]] += 1
        
        # 获取时间范围
        if messages:
            start_time = datetime.fromisoformat(messages[0]["timestamp"])
            end_time = datetime.fromisoformat(messages[-1]["timestamp"])
            time_range = f"{start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}"
        else:
            time_range = "未知"
        
        return {
            "total_messages": len(messages),
            "active_users": len(user_counts),
            "top_users": user_counts.most_common(5),
            "time_range": time_range
        }
    
    def _format_messages_for_ai(self, messages: list, max_messages: int = 100) -> str:
        """格式化消息供AI分析"""
        # 如果消息太多，采样
        if len(messages) > max_messages:
            # 均匀采样
            step = len(messages) // max_messages
            sampled = messages[::step][:max_messages]
        else:
            sampled = messages
        
        # 格式化为文本
        lines = []
        for msg in sampled:
            time = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M")
            lines.append(f"[{time}] {msg['username']}: {msg['message']}")
        
        return "\n".join(lines)
    
    def _generate_ai_summary(self, message_text: str, stats: dict) -> str:
        """使用AI生成总结"""
        prompt = f"""请总结以下群聊消息的重点内容：

消息数：{stats['total_messages']}条
参与人数：{stats['active_users']}人

聊天记录：
{message_text}

请提供简洁的总结，包含：
1. 🔥 主要话题（2-3个关键词）
2. 💬 重要内容（一句话概括）
3. 📌 关键结论（如果有）

要求：简洁明了，总共不超过100字。
"""
        
        try:
            # 使用临时用户ID生成总结（不保存历史）
            temp_user_id = "summary_bot_temp"
            
            # 清空临时用户的历史（确保每次都是新的总结）
            if temp_user_id in self.ai.conversations:
                self.ai.conversations[temp_user_id] = []
            
            # 调用AI生成总结
            summary = self.ai.chat(temp_user_id, prompt)
            
            # 清空临时用户的历史（不保存）
            if temp_user_id in self.ai.conversations:
                self.ai.conversations[temp_user_id] = []
            
            return summary
        except Exception as e:
            logger.error(f"AI总结生成失败: {e}")
            return "⚠️ AI总结生成失败，请稍后再试"
    
    def _format_final_summary(self, chat_title: str, stats: dict, ai_summary: str) -> str:
        """格式化最终总结"""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # 格式化活跃用户
        top_users_text = ""
        for username, count in stats["top_users"][:3]:
            top_users_text += f"  • {username}: {count}条\n"
        
        summary = f"""📊 群聊总结 ({today})

📍 群组：{chat_title}
⏰ 时间：{stats['time_range']}
💬 消息数：{stats['total_messages']}条
👥 活跃用户：{stats['active_users']}人

🏆 最活跃用户：
{top_users_text}
🤖 AI 总结：
{ai_summary}
"""
        
        return summary
    
    def generate_quick_summary(self, messages: list) -> str:
        """生成快速总结（不使用AI）"""
        if not messages:
            return "暂无消息"
        
        stats = self._calculate_stats(messages)
        
        summary = f"""📊 快速统计

消息数：{stats['total_messages']}条
活跃用户：{stats['active_users']}人
时间范围：{stats['time_range']}

最活跃用户：
"""
        
        for username, count in stats["top_users"][:5]:
            summary += f"  • {username}: {count}条\n"
        
        return summary

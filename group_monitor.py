"""
群消息监听模块
监听并存储群聊消息，用于后续总结
"""
import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger


class GroupMonitor:
    """群消息监听器"""
    
    def __init__(self, storage_dir="group_messages"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # 内存缓存 {chat_id: [messages]}
        self.message_cache = defaultdict(list)
        
        # 配置
        self.max_cache_size = 1000  # 每个群最多缓存消息数
        self.retention_days = 7  # 保留天数
    
    def record_message(self, chat_id: int, user_id: int, username: str, message: str):
        """记录群消息"""
        msg_data = {
            "user_id": user_id,
            "username": username,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # 添加到缓存
        self.message_cache[chat_id].append(msg_data)
        
        # 限制缓存大小
        if len(self.message_cache[chat_id]) > self.max_cache_size:
            self.message_cache[chat_id] = self.message_cache[chat_id][-self.max_cache_size:]
        
        # 定期保存到文件
        if len(self.message_cache[chat_id]) % 50 == 0:
            self._save_messages(chat_id)
    
    def _save_messages(self, chat_id: int):
        """保存消息到文件"""
        if not self.message_cache[chat_id]:
            return
        
        today = datetime.now().strftime("%Y-%m-%d")
        file_path = self.storage_dir / f"{chat_id}_{today}.json"
        
        try:
            # 读取已有数据
            existing_data = []
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
            
            # 合并新数据
            existing_data.extend(self.message_cache[chat_id])
            
            # 保存
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            # 清空缓存
            self.message_cache[chat_id] = []
            
            logger.debug(f"已保存群 {chat_id} 的消息")
        except Exception as e:
            logger.error(f"保存消息失败: {e}")
    
    def get_messages(self, chat_id: int, hours: int = 24) -> list:
        """获取指定时间范围内的消息"""
        messages = []
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # 从缓存获取
        for msg in self.message_cache[chat_id]:
            msg_time = datetime.fromisoformat(msg["timestamp"])
            if msg_time >= cutoff_time:
                messages.append(msg)
        
        # 从文件获取
        days_to_check = (hours // 24) + 2  # 多检查一天以防跨天
        for i in range(days_to_check):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            file_path = self.storage_dir / f"{chat_id}_{date}.json"
            
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_messages = json.load(f)
                    
                    for msg in file_messages:
                        msg_time = datetime.fromisoformat(msg["timestamp"])
                        if msg_time >= cutoff_time:
                            messages.append(msg)
                except Exception as e:
                    logger.error(f"读取消息文件失败: {e}")
        
        # 按时间排序
        messages.sort(key=lambda x: x["timestamp"])
        
        return messages
    
    def get_chat_stats(self, chat_id: int, hours: int = 24) -> dict:
        """获取群聊统计信息"""
        messages = self.get_messages(chat_id, hours)
        
        if not messages:
            return {
                "total_messages": 0,
                "active_users": 0,
                "user_stats": {}
            }
        
        # 统计用户消息数
        user_stats = defaultdict(int)
        for msg in messages:
            user_stats[msg["username"]] += 1
        
        return {
            "total_messages": len(messages),
            "active_users": len(user_stats),
            "user_stats": dict(sorted(user_stats.items(), key=lambda x: x[1], reverse=True)),
            "time_range": f"{hours}小时"
        }
    
    def cleanup_old_messages(self):
        """清理过期消息"""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        
        for file_path in self.storage_dir.glob("*.json"):
            try:
                # 从文件名提取日期
                date_str = file_path.stem.split("_")[-1]
                file_date = datetime.strptime(date_str, "%Y-%m-%d")
                
                if file_date < cutoff_date:
                    file_path.unlink()
                    logger.info(f"已删除过期消息文件: {file_path.name}")
            except Exception as e:
                logger.error(f"清理文件失败: {e}")
    
    def save_all(self):
        """保存所有缓存的消息"""
        for chat_id in list(self.message_cache.keys()):
            if self.message_cache[chat_id]:
                self._save_messages(chat_id)

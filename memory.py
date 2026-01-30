"""
记忆系统模块
记录和管理用户的重要信息
"""
import json
from pathlib import Path
from datetime import datetime
from loguru import logger


class MemoryManager:
    """记忆管理器"""
    
    def __init__(self, memory_dir="chat_history"):
        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(exist_ok=True)
        self.memory_file = self.memory_dir / "user_memories.json"
        self.memories = self._load_memories()
    
    def _load_memories(self) -> dict:
        """加载记忆数据"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载记忆数据失败: {e}")
                return {}
        return {}
    
    def _save_memories(self):
        """保存记忆数据"""
        try:
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                json.dump(self.memories, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存记忆数据失败: {e}")
    
    def add_memory(self, user_id: str, key: str, value: str):
        """添加记忆"""
        if user_id not in self.memories:
            self.memories[user_id] = {}
        
        self.memories[user_id][key] = {
            "value": value,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        self._save_memories()
        logger.info(f"用户 {user_id} 添加记忆: {key} = {value}")
    
    def update_memory(self, user_id: str, key: str, value: str):
        """更新记忆"""
        if user_id not in self.memories:
            self.memories[user_id] = {}
        
        if key in self.memories[user_id]:
            self.memories[user_id][key]["value"] = value
            self.memories[user_id][key]["updated_at"] = datetime.now().isoformat()
        else:
            self.add_memory(user_id, key, value)
        
        self._save_memories()
        logger.info(f"用户 {user_id} 更新记忆: {key} = {value}")
    
    def get_memory(self, user_id: str, key: str) -> str:
        """获取单个记忆"""
        if user_id in self.memories and key in self.memories[user_id]:
            return self.memories[user_id][key]["value"]
        return None
    
    def get_all_memories(self, user_id: str) -> dict:
        """获取用户所有记忆"""
        return self.memories.get(user_id, {})
    
    def delete_memory(self, user_id: str, key: str) -> bool:
        """删除记忆"""
        if user_id in self.memories and key in self.memories[user_id]:
            del self.memories[user_id][key]
            self._save_memories()
            logger.info(f"用户 {user_id} 删除记忆: {key}")
            return True
        return False
    
    def clear_memories(self, user_id: str):
        """清空用户所有记忆"""
        if user_id in self.memories:
            self.memories[user_id] = {}
            self._save_memories()
            logger.info(f"用户 {user_id} 清空了所有记忆")
    
    def get_memory_context(self, user_id: str) -> str:
        """获取记忆上下文（用于注入到对话）"""
        memories = self.get_all_memories(user_id)
        
        if not memories:
            return ""
        
        memory_lines = []
        for key, data in memories.items():
            memory_lines.append(f"- {key}: {data['value']}")
        
        context = "关于用户的记忆：\n" + "\n".join(memory_lines)
        return context
    
    def format_memories(self, user_id: str) -> str:
        """格式化记忆为文本"""
        memories = self.get_all_memories(user_id)
        
        if not memories:
            return "🧠 还没有记住任何信息哦"
        
        lines = ["🧠 我记住的关于你的信息：\n"]
        for key, data in memories.items():
            value = data["value"]
            created = datetime.fromisoformat(data["created_at"]).strftime("%Y-%m-%d")
            lines.append(f"• {key}: {value}")
            lines.append(f"  （记录于 {created}）")
        
        lines.append(f"\n💡 使用 /forget 关键词 可以删除记忆")
        
        return "\n".join(lines)
    
    def extract_and_save(self, user_id: str, message: str, reply: str):
        """从对话中提取并保存重要信息（简单实现）"""
        # 简单的关键词匹配
        keywords = {
            "名字": ["我叫", "我的名字是", "叫我"],
            "年龄": ["我今年", "岁了", "我的年龄"],
            "职业": ["我是", "我做", "我的工作"],
            "爱好": ["我喜欢", "我爱", "我的爱好"],
            "生日": ["我的生日", "生日是"],
        }
        
        for key, patterns in keywords.items():
            for pattern in patterns:
                if pattern in message:
                    # 提取信息（简单实现，可以用 AI 提取更准确）
                    # 这里只是示例，实际可以调用 AI 来提取
                    pass

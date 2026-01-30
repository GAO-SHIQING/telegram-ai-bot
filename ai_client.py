import json
import time
from pathlib import Path
from openai import OpenAI
from loguru import logger
from config import OPENAI_API_KEY, OPENAI_BASE_URL, MODEL_NAME, MAX_API_RETRY, HISTORY_DIR
from config import VISION_MODEL_NAME
from personas import get_persona, DEFAULT_PERSONA
from stats import StatsManager
from memory import MemoryManager
from search import SearchManager


class AIClient:
    """AI 客户端，负责与 AI API 交互和管理对话历史"""
    
    def __init__(self, api_key=None, base_url=None, model_name=None, max_retry=None, history_dir=None):
        # 使用传入的参数或默认配置
        self.api_key = api_key or OPENAI_API_KEY
        self.base_url = base_url or OPENAI_BASE_URL
        self.model_name = model_name or MODEL_NAME
        self.vision_model_name = VISION_MODEL_NAME  # 视觉模型
        self.max_retry = max_retry or MAX_API_RETRY
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 对话历史缓存 {user_id: [messages]}
        self.conversations = {}
        # 用户人设选择 {user_id: persona_key}
        self.user_personas = {}
        # 统计管理器
        self.stats = StatsManager(history_dir or HISTORY_DIR)
        # 记忆管理器
        self.memory = MemoryManager(history_dir or HISTORY_DIR)
        # 搜索管理器
        self.search = SearchManager()
        # 保留最近N轮对话
        self.max_history = 10
        
        # 创建历史记录目录
        self.history_dir = Path(history_dir or HISTORY_DIR)
        self.history_dir.mkdir(exist_ok=True)
        
        # 加载数据
        self._load_all_histories()
        self._load_user_personas()

    def _get_history_file(self, user_id: str) -> Path:
        """获取用户历史记录文件路径"""
        # 使用安全的文件名
        safe_name = "".join(c if c.isalnum() or c in ('-', '_') else '_' for c in user_id)
        return self.history_dir / f"{safe_name}.json"
    
    def _get_personas_file(self) -> Path:
        """获取用户人设配置文件路径"""
        return self.history_dir / "user_personas.json"
    
    def _load_user_personas(self):
        """加载用户人设配置"""
        personas_file = self._get_personas_file()
        
        if personas_file.exists():
            try:
                with open(personas_file, 'r', encoding='utf-8') as f:
                    self.user_personas = json.load(f)
                logger.info(f"已加载 {len(self.user_personas)} 个用户的人设配置")
            except Exception as e:
                logger.warning(f"加载用户人设配置失败: {e}")
                self.user_personas = {}
        else:
            self.user_personas = {}
    
    def _save_user_personas(self):
        """保存用户人设配置"""
        personas_file = self._get_personas_file()
        
        try:
            with open(personas_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_personas, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存用户人设配置失败: {e}")
    
    def get_user_persona(self, user_id: str) -> str:
        """获取用户当前人设"""
        return self.user_personas.get(user_id, DEFAULT_PERSONA)
    
    def set_user_persona(self, user_id: str, persona_key: str):
        """设置用户人设"""
        self.user_personas[user_id] = persona_key
        self._save_user_personas()
        logger.info(f"用户 {user_id} 切换人设为: {persona_key}")
    
    def _load_history(self, user_id: str):
        """加载单个用户的对话历史"""
        history_file = self._get_history_file(user_id)
        
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.conversations[user_id] = json.load(f)
                logger.debug(f"加载历史记录: {user_id}")
            except Exception as e:
                logger.warning(f"加载历史记录失败 [{user_id}]: {e}")
                self.conversations[user_id] = []
        else:
            self.conversations[user_id] = []
    
    def _load_all_histories(self):
        """加载所有历史记录"""
        if not self.history_dir.exists():
            return
        
        # 需要跳过的配置文件
        skip_files = {"user_personas.json", "user_stats.json", "user_memories.json"}
        
        count = 0
        for history_file in self.history_dir.glob("*.json"):
            # 跳过配置文件
            if history_file.name in skip_files:
                continue
                
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    user_id = history_file.stem
                    self.conversations[user_id] = json.load(f)
                    count += 1
            except Exception as e:
                logger.warning(f"加载历史记录失败 [{history_file.name}]: {e}")
        
        if count > 0:
            logger.info(f"已加载 {count} 个用户的历史记录")
    
    def _save_history(self, user_id: str):
        """保存单个用户的对话历史"""
        history_file = self._get_history_file(user_id)
        
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.conversations.get(user_id, []), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存历史记录失败 [{user_id}]: {e}")

    async def transcribe_audio(self, audio_bytes) -> str:
        """语音转文字"""
        try:
            # 保存临时文件
            import tempfile
            with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp_file:
                temp_file.write(audio_bytes.read())
                temp_path = temp_file.name
            
            # 调用 Whisper API
            with open(temp_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="zh"
                )
            
            # 删除临时文件
            import os
            os.unlink(temp_path)
            
            return transcript.text
            
        except Exception as e:
            logger.error(f"语音转文字失败: {e}")
            return None
    
    async def chat_with_image(self, user_id: str, message: str, image_bytes) -> str:
        """与 AI 对话（带图片）"""
        import base64
        
        # 获取或初始化对话历史
        if user_id not in self.conversations:
            self._load_history(user_id)
        
        history = self.conversations[user_id]
        
        # 首次对话，记录对话次数（历史为空表示新对话）
        if len(history) == 0:
            self.stats.record_conversation(user_id)
        
        # 获取用户当前人设
        persona_key = self.get_user_persona(user_id)
        persona = get_persona(persona_key)
        current_prompt = persona['prompt']
        
        # 获取记忆上下文
        memory_context = self.memory.get_memory_context(user_id)
        if memory_context:
            current_prompt = f"{current_prompt}\n\n{memory_context}"
        
        # 记录消息统计
        self.stats.record_message(user_id, persona_key)
        
        # 将图片转为 base64
        image_base64 = base64.b64encode(image_bytes.read()).decode('utf-8')
        
        # 构建消息（包含历史对话）
        messages = [{"role": "system", "content": current_prompt}]
        
        # 添加历史对话
        messages.extend(history)
        
        # 添加当前图片消息
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": message},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                }
            ]
        })
        
        # 重试机制
        last_error = None
        for attempt in range(self.max_retry):
            try:
                # 使用视觉模型（图片识别专用）
                response = self.client.chat.completions.create(
                    model=self.vision_model_name,  # 使用视觉模型
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                    timeout=90  # 视觉模型可能需要更长时间
                )
                
                reply = response.choices[0].message.content.strip()
                
                # 保存文字交互到历史记录（不保存图片base64）
                history.append({"role": "user", "content": f"[发送了图片] {message}"})
                history.append({"role": "assistant", "content": reply})
                
                # 限制历史长度
                if len(history) > self.max_history * 2:
                    self.conversations[user_id] = history[-self.max_history * 2:]
                
                # 保存历史记录
                self._save_history(user_id)
                
                return reply
                
            except Exception as e:
                last_error = e
                error_msg = str(e)
                
                # 检查是否是模型不存在的错误
                if "does not exist" in error_msg or "Model not found" in error_msg:
                    logger.error(f"视觉模型不存在: {self.vision_model_name}")
                    return "暂时看不了图片|||等会再试试吧"
                
                # 超时错误不重试太多次
                if "timeout" in error_msg.lower() or "timed out" in error_msg.lower():
                    logger.warning(f"图片识别超时 ({attempt + 1}/{self.max_retry})")
                    if attempt < 1:
                        time.sleep(2)
                        continue
                    else:
                        break
                
                # 其他错误正常重试
                if attempt < self.max_retry - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"AI 图片识别失败，重试 ({attempt + 1}/{self.max_retry})，等待 {wait_time}s")
                    time.sleep(wait_time)
                else:
                    logger.error(f"AI 图片识别失败，已达最大重试次数")
        
        # 返回友好的错误提示（不包含技术细节）
        if "timeout" in str(last_error).lower() or "timed out" in str(last_error).lower():
            return "图片识别超时了|||稍后再试试吧"
        else:
            return "图片识别失败了|||请稍后再试"
    
    def chat(self, user_id: str, message: str) -> str:
        """与 AI 对话（带重试机制）"""
        # 获取或初始化对话历史
        if user_id not in self.conversations:
            self._load_history(user_id)
        
        history = self.conversations[user_id]
        
        # 首次对话，记录对话次数（历史为空表示新对话）
        if len(history) == 0:
            self.stats.record_conversation(user_id)
        
        # 获取用户当前人设
        persona_key = self.get_user_persona(user_id)
        persona = get_persona(persona_key)
        current_prompt = persona['prompt']
        
        # 获取记忆上下文
        memory_context = self.memory.get_memory_context(user_id)
        if memory_context:
            current_prompt = f"{current_prompt}\n\n{memory_context}"
        
        # 记录消息统计
        self.stats.record_message(user_id, persona_key)
        
        # 构建消息列表
        messages = [{"role": "system", "content": current_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": message})

        # 重试机制
        last_error = None
        for attempt in range(self.max_retry):
            try:
                # 调用 AI（设置合理的超时）
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=messages,
                    max_tokens=1000,
                    temperature=0.7,
                    timeout=60  # 增加到60秒，避免频繁超时
                )
                
                reply = response.choices[0].message.content.strip()
                
                # 更新对话历史
                history.append({"role": "user", "content": message})
                history.append({"role": "assistant", "content": reply})
                
                # 限制历史长度
                if len(history) > self.max_history * 2:
                    self.conversations[user_id] = history[-self.max_history * 2:]
                
                # 保存历史记录
                self._save_history(user_id)
                
                return reply
                
            except Exception as e:
                last_error = e
                error_type = type(e).__name__
                
                # 超时错误不重试太多次
                if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                    logger.warning(f"AI 调用超时 ({attempt + 1}/{self.max_retry}): {e}")
                    if attempt < 1:  # 超时只重试1次
                        time.sleep(2)
                        continue
                    else:
                        break
                
                # 其他错误正常重试
                if attempt < self.max_retry - 1:
                    wait_time = 2 ** attempt  # 指数退避：1s, 2s, 4s
                    logger.warning(f"AI 调用失败，重试 ({attempt + 1}/{self.max_retry})，等待 {wait_time}s: {error_type}")
                    time.sleep(wait_time)
                else:
                    logger.error(f"AI 调用失败，已达最大重试次数: {error_type} - {e}")
        
        # 根据错误类型返回不同的提示
        if "timeout" in str(last_error).lower() or "timed out" in str(last_error).lower():
            return "网络有点慢|||稍后再试试吧"
        else:
            return "出了点问题|||等会再试试吧"
        
        return f"抱歉，我暂时无法回复（{last_error}），请稍后再试~"

    def clear_history(self, user_id: str):
        """清除某用户的对话历史"""
        if user_id in self.conversations:
            self.conversations[user_id] = []
            self._save_history(user_id)
            logger.info(f"已清空历史记录: {user_id}")

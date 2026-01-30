"""
Telegram AI 机器人
基于 python-telegram-bot + AI 的智能对话机器人，支持多人设切换
"""
import asyncio
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from loguru import logger

from ai_client import AIClient
from config import TELEGRAM_BOT_TOKEN, BOT_NAME
from personas import get_persona_list, is_valid_persona, get_persona


class TelegramBot:
    """Telegram AI 机器人"""
    
    def __init__(self):
        self.ai = AIClient()
        self.app = None
        logger.info("✓ 机器人初始化完成")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /start 命令"""
        user = update.effective_user
        user_id = str(user.id)
        
        # 获取用户当前人设
        persona_key = self.ai.get_user_persona(user_id)
        persona = get_persona(persona_key)
        
        # 创建快捷按钮
        keyboard = [
            [
                InlineKeyboardButton("🎭 切换人设", callback_data="show_personas"),
                InlineKeyboardButton("📊 使用统计", callback_data="stats")
            ],
            [
                InlineKeyboardButton("🧠 查看记忆", callback_data="memory"),
                InlineKeyboardButton("🔍 搜索", switch_inline_query_current_chat="")
            ],
            [
                InlineKeyboardButton("❓ 帮助", callback_data="help"),
                InlineKeyboardButton("🗑️ 清空历史", callback_data="clear")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_msg = (
            f"你好 {user.first_name}！\n\n"
            f"我是 {BOT_NAME}，一个 AI 聊天助手。\n"
            f"当前人设：{persona['name']}\n\n"
            f"💬 直接发消息给我就可以聊天\n"
            f"📝 点击下方按钮快速操作："
        )
        await update.message.reply_text(welcome_msg, reply_markup=reply_markup)
        logger.info(f"用户 {user.id} ({user.first_name}) 启动了机器人")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /help 命令"""
        help_msg = (
            f"🤖 {BOT_NAME} 使用帮助\n\n"
            f"💬 聊天方式：\n"
            f"  直接发送消息即可开始对话\n"
            f"  我会记住我们的对话历史\n\n"
            f"📝 可用命令：\n"
            f"  /start - 显示欢迎信息\n"
            f"  /help - 显示此帮助\n"
            f"  /persona - 查看和切换人设\n"
            f"  /persona 小高 - 切换到小高同学\n"
            f"  /persona 丰子 - 切换到丰子\n"
            f"  /stats - 查看使用统计\n"
            f"  /memory - 查看记住的信息\n"
            f"  /memory 名字 小明 - 记住信息\n"
            f"  /forget 名字 - 忘记信息\n"
            f"  /search Python教程 - 联网搜索\n"
            f"  /clear - 清空对话历史\n\n"
            f"✨ 特点：\n"
            f"  • 多种人设可选，风格各异\n"
            f"  • 记住上下文，支持连续对话\n"
            f"  • 快速响应，实时回复\n"
        )
        await update.message.reply_text(help_msg)
    
    async def clear_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /clear 命令"""
        user_id = str(update.effective_user.id)
        self.ai.clear_history(user_id)
        await update.message.reply_text("✅ 对话历史已清空")
        logger.info(f"用户 {user_id} 清空了对话历史")
    
    async def persona_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /persona 命令"""
        user_id = str(update.effective_user.id)
        
        # 如果有参数，尝试切换人设
        if context.args:
            persona_key = context.args[0]
            
            if is_valid_persona(persona_key):
                # 切换人设
                self.ai.set_user_persona(user_id, persona_key)
                persona = get_persona(persona_key)
                
                # 清空历史记录（切换人设时建议清空）
                self.ai.clear_history(user_id)
                
                await update.message.reply_text(
                    f"✅ 已切换到：{persona['name']}\n"
                    f"📝 {persona['description']}\n\n"
                    f"对话历史已自动清空，可以开始新的对话了~"
                )
                logger.info(f"用户 {user_id} 切换人设为: {persona_key}")
            else:
                await update.message.reply_text(
                    f"❌ 未知的人设：{persona_key}\n\n"
                    f"{get_persona_list()}\n\n"
                    f"使用方法：/persona 小高"
                )
        else:
            # 显示人设选择按钮
            await self._show_persona_keyboard(update, user_id)
    
    async def _show_persona_keyboard(self, update, user_id):
        """显示人设选择键盘"""
        current_key = self.ai.get_user_persona(user_id)
        current_persona = get_persona(current_key)
        
        # 创建人设选择按钮
        keyboard = [
            [
                InlineKeyboardButton("👨 小高同学", callback_data="persona_小高"),
                InlineKeyboardButton("👩 丰子", callback_data="persona_丰子")
            ],
            [
                InlineKeyboardButton("🤖 小助手", callback_data="persona_小助手"),
                InlineKeyboardButton("😄 逗比", callback_data="persona_逗比")
            ],
            [
                InlineKeyboardButton("📚 学霸", callback_data="persona_学霸")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        msg = (
            f"🎭 当前人设：{current_persona['name']}\n"
            f"📝 {current_persona['description']}\n\n"
            f"点击下方按钮切换人设："
        )
        
        # 判断是从命令调用还是从按钮回调调用
        if hasattr(update, 'callback_query') and update.callback_query:
            # 从按钮回调调用，编辑原消息
            await update.callback_query.message.edit_text(msg, reply_markup=reply_markup)
        else:
            # 从命令调用，发送新消息
            await update.message.reply_text(msg, reply_markup=reply_markup)
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /stats 命令"""
        user_id = str(update.effective_user.id)
        stats_text = self.ai.stats.format_stats(user_id)
        await update.message.reply_text(stats_text)
        logger.info(f"用户 {user_id} 查看了统计信息")
    
    async def memory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /memory 命令"""
        user_id = str(update.effective_user.id)
        
        # 如果有参数，添加记忆
        if context.args and len(context.args) >= 2:
            key = context.args[0]
            value = " ".join(context.args[1:])
            self.ai.memory.add_memory(user_id, key, value)
            await update.message.reply_text(f"✅ 已记住：{key} = {value}")
            logger.info(f"用户 {user_id} 添加记忆: {key}")
        else:
            # 显示所有记忆
            memory_text = self.ai.memory.format_memories(user_id)
            await update.message.reply_text(memory_text)
    
    async def forget_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /forget 命令"""
        user_id = str(update.effective_user.id)
        
        if context.args:
            key = context.args[0]
            if self.ai.memory.delete_memory(user_id, key):
                await update.message.reply_text(f"✅ 已忘记：{key}")
                logger.info(f"用户 {user_id} 删除记忆: {key}")
            else:
                await update.message.reply_text(f"❌ 没有找到：{key}")
        else:
            await update.message.reply_text("请指定要忘记的内容，例如：/forget 名字")
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理 /search 命令"""
        user_id = str(update.effective_user.id)
        
        if not context.args:
            await update.message.reply_text("请输入搜索内容，例如：/search Python教程")
            return
        
        query = " ".join(context.args)
        logger.info(f"用户 {user_id} 搜索: {query}")
        
        # 发送"正在输入"状态
        await update.message.chat.send_action("typing")
        
        try:
            # 执行搜索
            results = self.ai.search.search_web(query, max_results=3)
            result_text = self.ai.search.format_search_results(results)
            
            await update.message.reply_text(result_text)
            logger.success(f"搜索完成: {query}")
            
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            await update.message.reply_text("抱歉，搜索失败了，请稍后再试~")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理按钮回调"""
        query = update.callback_query
        await query.answer()
        
        user_id = str(query.from_user.id)
        data = query.data
        
        # 处理不同的按钮
        if data == "show_personas":
            # 传递 update 而不是 query
            await self._show_persona_keyboard(update, user_id)
        
        elif data.startswith("persona_"):
            persona_key = data.replace("persona_", "")
            if is_valid_persona(persona_key):
                self.ai.set_user_persona(user_id, persona_key)
                persona = get_persona(persona_key)
                self.ai.clear_history(user_id)
                
                await query.message.edit_text(
                    f"✅ 已切换到：{persona['name']}\n"
                    f"📝 {persona['description']}\n\n"
                    f"对话历史已自动清空，可以开始新的对话了~"
                )
                logger.info(f"用户 {user_id} 切换人设为: {persona_key}")
        
        elif data == "stats":
            stats_text = self.ai.stats.format_stats(user_id)
            await query.message.edit_text(stats_text)
        
        elif data == "memory":
            memory_text = self.ai.memory.format_memories(user_id)
            await query.message.edit_text(memory_text)
        
        elif data == "help":
            help_msg = (
                f"🤖 {BOT_NAME} 使用帮助\n\n"
                f"💬 聊天方式：\n"
                f"  直接发送消息即可开始对话\n"
                f"  我会记住我们的对话历史\n\n"
                f"📝 可用命令：\n"
                f"  /start - 显示欢迎信息\n"
                f"  /help - 显示此帮助\n"
                f"  /persona - 查看和切换人设\n"
                f"  /stats - 查看使用统计\n"
                f"  /memory - 查看记住的信息\n"
                f"  /memory 名字 小明 - 记住信息\n"
                f"  /forget 名字 - 忘记信息\n"
                f"  /search Python教程 - 联网搜索\n"
                f"  /clear - 清空对话历史\n\n"
                f"✨ 特点：\n"
                f"  • 多种人设可选，风格各异\n"
                f"  • 记住上下文，支持连续对话\n"
                f"  • 快速响应，实时回复\n"
            )
            await query.message.edit_text(help_msg)
        
        elif data == "clear":
            self.ai.clear_history(user_id)
            await query.message.edit_text("✅ 对话历史已清空")
            logger.info(f"用户 {user_id} 清空了对话历史")
        
        elif data == "stats":
            stats_text = self.ai.stats.format_stats(user_id)
            await query.message.edit_text(stats_text)
        
        elif data == "memory":
            memory_text = self.ai.memory.format_memories(user_id)
            await query.message.edit_text(memory_text)
        
        elif data == "help":
            help_msg = (
                f"🤖 {BOT_NAME} 使用帮助\n\n"
                f"💬 聊天方式：\n"
                f"  直接发送消息即可开始对话\n"
                f"  我会记住我们的对话历史\n\n"
                f"📝 可用命令：\n"
                f"  /start - 显示欢迎信息\n"
                f"  /help - 显示此帮助\n"
                f"  /persona - 查看和切换人设\n"
                f"  /stats - 查看使用统计\n"
                f"  /memory - 查看记住的信息\n"
                f"  /memory 名字 小明 - 记住信息\n"
                f"  /forget 名字 - 忘记信息\n"
                f"  /search Python教程 - 联网搜索\n"
                f"  /clear - 清空对话历史\n\n"
                f"✨ 特点：\n"
                f"  • 多种人设可选，风格各异\n"
                f"  • 记住上下文，支持连续对话\n"
                f"  • 快速响应，实时回复\n"
            )
            await query.message.edit_text(help_msg)
        
        elif data == "clear":
            self.ai.clear_history(user_id)
            await query.message.edit_text("✅ 对话历史已清空")
            logger.info(f"用户 {user_id} 清空了对话历史")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理普通消息"""
        user = update.effective_user
        user_id = str(user.id)
        message_text = update.message.text
        chat_type = update.message.chat.type
        
        # 群聊判断：只在被 @ 或回复时响应
        if chat_type in ["group", "supergroup"]:
            bot_username = context.bot.username
            # 检查是否 @ 了机器人
            is_mentioned = f"@{bot_username}" in message_text
            # 检查是否回复了机器人的消息
            is_reply = update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id
            
            if not (is_mentioned or is_reply):
                return  # 群聊中未 @ 机器人，不响应
            
            # 移除 @ 标记
            message_text = message_text.replace(f"@{bot_username}", "").strip()
        
        logger.info(f"收到消息 [{user.first_name}]: {message_text[:50]}...")
        
        # 发送"正在输入"状态
        await update.message.chat.send_action("typing")
        
        try:
            # 在异步环境中运行同步的 AI 调用
            import asyncio
            loop = asyncio.get_event_loop()
            
            # 使用 run_in_executor 避免阻塞
            reply = await loop.run_in_executor(
                None,  # 使用默认线程池
                self.ai.chat,
                user_id,
                message_text
            )
            
            # 处理分条发送（用 ||| 分隔）
            if "|||" in reply:
                parts = [p.strip() for p in reply.split("|||") if p.strip()]
                for part in parts:
                    await update.message.reply_text(part)
                    await asyncio.sleep(0.5)  # 分条发送间隔
            else:
                await update.message.reply_text(reply)
            
            logger.success(f"已回复 [{user.first_name}]: {reply[:50]}...")
            
        except asyncio.TimeoutError:
            logger.error(f"AI 响应超时 [{user.first_name}]")
            await update.message.reply_text("网络有点慢|||稍后再试试吧")
        except Exception as e:
            error_type = type(e).__name__
            logger.error(f"处理消息失败 [{user.first_name}]: {error_type} - {e}")
            
            # 根据错误类型给出不同提示
            if "timeout" in str(e).lower() or "timed out" in str(e).lower():
                await update.message.reply_text("网络有点慢|||稍后再试试吧")
            else:
                await update.message.reply_text("出了点问题|||等会再试试吧")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理图片消息"""
        user = update.effective_user
        user_id = str(user.id)
        chat_type = update.message.chat.type
        
        # 群聊判断
        if chat_type in ["group", "supergroup"]:
            bot_username = context.bot.username
            caption = update.message.caption or ""
            is_mentioned = f"@{bot_username}" in caption
            is_reply = update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id
            
            if not (is_mentioned or is_reply):
                return
        
        logger.info(f"收到图片 [{user.first_name}]")
        
        # 发送"正在输入"状态
        await update.message.chat.send_action("typing")
        
        try:
            # 获取图片
            photo = update.message.photo[-1]  # 获取最大尺寸的图片
            photo_file = await photo.get_file()
            
            # 下载图片
            import io
            photo_bytes = io.BytesIO()
            await photo_file.download_to_memory(photo_bytes)
            photo_bytes.seek(0)
            
            # 获取图片说明文字
            caption = update.message.caption or "这是什么"
            
            # 调用 AI 识别图片
            reply = await self.ai.chat_with_image(user_id, caption, photo_bytes)
            
            # 处理分条发送
            if "|||" in reply:
                parts = [p.strip() for p in reply.split("|||") if p.strip()]
                for part in parts:
                    await update.message.reply_text(part)
                    await asyncio.sleep(0.5)
            else:
                await update.message.reply_text(reply)
            
            logger.success(f"已回复图片 [{user.first_name}]")
            
        except Exception as e:
            logger.error(f"处理图片失败: {e}")
            await update.message.reply_text("抱歉，图片识别失败了，请稍后再试~")
    
    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理语音消息"""
        user = update.effective_user
        user_id = str(user.id)
        chat_type = update.message.chat.type
        
        # 群聊判断
        if chat_type in ["group", "supergroup"]:
            bot_username = context.bot.username
            is_reply = update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id
            
            if not is_reply:
                return
        
        logger.info(f"收到语音 [{user.first_name}]")
        
        # 发送"正在输入"状态
        await update.message.chat.send_action("typing")
        
        try:
            # 获取语音文件
            if update.message.voice:
                voice_file = await update.message.voice.get_file()
            else:
                voice_file = await update.message.audio.get_file()
            
            # 下载语音
            import io
            voice_bytes = io.BytesIO()
            await voice_file.download_to_memory(voice_bytes)
            voice_bytes.seek(0)
            
            # 转换语音为文字
            text = await self.ai.transcribe_audio(voice_bytes)
            
            if not text:
                await update.message.reply_text("抱歉，没有识别到语音内容~")
                return
            
            logger.info(f"语音识别结果: {text[:50]}...")
            
            # 调用 AI 生成回复
            reply = self.ai.chat(user_id, text)
            
            # 处理分条发送
            if "|||" in reply:
                parts = [p.strip() for p in reply.split("|||") if p.strip()]
                for part in parts:
                    await update.message.reply_text(part)
                    await asyncio.sleep(0.5)
            else:
                await update.message.reply_text(reply)
            
            logger.success(f"已回复语音 [{user.first_name}]")
            
        except Exception as e:
            logger.error(f"处理语音失败: {e}")
            await update.message.reply_text("抱歉，语音识别失败了，请稍后再试~")
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """处理错误"""
        error = context.error
        error_type = type(error).__name__
        
        # 网络相关错误，只记录警告，不打扰用户
        network_errors = ["RemoteProtocolError", "NetworkError", "TimedOut", "TimeoutError"]
        if any(err in error_type for err in network_errors):
            logger.warning(f"网络错误（自动重试）: {error_type} - {error}")
            return
        
        # 按钮超时错误，忽略
        if "Query is too old" in str(error) or "query id is invalid" in str(error):
            logger.debug(f"按钮超时（忽略）: {error}")
            return
        
        # 其他错误记录详细信息
        logger.error(f"更新处理出错: {error_type} - {error}")
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "抱歉，处理你的消息时出错了，请稍后再试~"
                )
            except Exception as e:
                logger.error(f"发送错误消息失败: {e}")
    
    def start(self):
        """启动机器人"""
        logger.info("=" * 70)
        logger.info(f"🤖 {BOT_NAME} Telegram Bot 启动中...")
        logger.info("=" * 70)
        
        # 创建应用，增加连接配置和代理支持
        from config import PROXY_URL
        builder = (
            Application.builder()
            .token(TELEGRAM_BOT_TOKEN)
            .connect_timeout(30.0)
            .read_timeout(30.0)
            .write_timeout(30.0)
            .pool_timeout(30.0)
        )
        
        # 如果配置了代理，则使用代理
        if PROXY_URL:
            builder = builder.proxy_url(PROXY_URL)
            logger.info(f"✓ 使用代理: {PROXY_URL}")
        
        self.app = builder.build()
        
        # 注册命令处理器
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("persona", self.persona_command))
        self.app.add_handler(CommandHandler("stats", self.stats_command))
        self.app.add_handler(CommandHandler("memory", self.memory_command))
        self.app.add_handler(CommandHandler("forget", self.forget_command))
        self.app.add_handler(CommandHandler("search", self.search_command))
        self.app.add_handler(CommandHandler("clear", self.clear_command))
        
        # 注册按钮回调处理器
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # 注册消息处理器
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, self.handle_voice))
        
        # 注册错误处理器
        self.app.add_error_handler(self.error_handler)
        
        # 设置机器人命令列表（在输入 / 时显示）
        async def set_commands(app):
            commands = [
                BotCommand("start", "显示欢迎信息和快捷按钮"),
                BotCommand("help", "显示帮助信息"),
                BotCommand("persona", "查看和切换人设"),
                BotCommand("stats", "查看使用统计"),
                BotCommand("memory", "查看记住的信息"),
                BotCommand("forget", "忘记某个信息"),
                BotCommand("search", "联网搜索"),
                BotCommand("clear", "清空对话历史")
            ]
            await app.bot.set_my_commands(commands)
            logger.info("✓ 已设置机器人命令列表")
        
        # 在启动后设置命令
        self.app.post_init = set_commands
        
        # 添加心跳日志（每小时记录一次）
        from datetime import datetime
        async def heartbeat(context):
            logger.info(f"💓 心跳检测 - 机器人运行正常 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
        
        # 设置定时任务（每小时）
        from telegram.ext import JobQueue
        job_queue = self.app.job_queue
        if job_queue:
            job_queue.run_repeating(heartbeat, interval=3600, first=3600)  # 3600秒 = 1小时
        
        logger.info("")
        logger.info("✨ 功能特性:")
        logger.info("  ✅ 5种人设可选（小高、丰子、小助手、逗比、学霸）")
        logger.info("  ✅ 图片识别，发送图片即可识别")
        logger.info("  ✅ 语音识别，发送语音自动转文字")
        logger.info("  ✅ 联网搜索，获取实时信息")
        logger.info("  ✅ 记忆系统，记住你的重要信息")
        logger.info("  ✅ 使用统计，了解你的聊天习惯")
        logger.info("  ✅ 群聊支持，@ 机器人即可对话")
        logger.info("  ✅ 记住上下文，支持连续对话")
        logger.info("  ✅ 快速响应，实时回复")
        logger.info("  ✅ 支持分条发送消息")
        logger.info("")
        logger.info("🚀 机器人已启动，等待消息...")
        logger.info("💡 提示：网络错误会自动重试，无需担心")
        logger.info("按 Ctrl+C 停止")
        logger.info("=" * 70)
        logger.info("")
        
        # 启动轮询，增加健壮性配置
        try:
            self.app.run_polling(
                allowed_updates=Update.ALL_TYPES,
                drop_pending_updates=True,  # 跳过启动前的旧消息
                poll_interval=1.0,  # 轮询间隔（秒）
                timeout=10,  # 长轮询超时（秒）
                bootstrap_retries=-1,  # 无限重试连接
                read_timeout=30,  # 读取超时
                write_timeout=30,  # 写入超时
                connect_timeout=30,  # 连接超时
                pool_timeout=30  # 连接池超时
            )
        except Exception as e:
            logger.error(f"轮询出错: {e}")
            raise
    
    def stop(self):
        """停止机器人"""
        logger.info("🛑 机器人已停止")


def main():
    bot = TelegramBot()
    try:
        bot.start()
    except KeyboardInterrupt:
        logger.info("\n收到停止信号")
        bot.stop()
    except Exception as e:
        logger.error(f"机器人运行出错: {e}")
        bot.stop()


if __name__ == "__main__":
    main()

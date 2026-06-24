# 图片审查插件 (带配置面板版) for AstrBot 安卓 1.5.3

import logging
from astrbot.core.star.star_handler import star_handler
from astrbot.core.platform.astrbot_message_event import AstrBotMessageEvent
from astrbot.core.star.star_plugin import star_plugin

# 1. 定义配置面板结构
@star_plugin("图片审查助手", "2.0.0")
class ImageCheckPlugin:
    def __init__(self, bot):
        self.bot = bot
        # 默认配置项（请在网页面板里修改）
        self.config = {
            "provider_name": "openai",  # 👈 这里填你大模型提供商的名字
            "mute_duration": 10,        # 👈 禁言时长（分钟），填0表示只撤回不禁言
            "check_threshold": "严格"   # 👈 敏感度：严格/宽松
        }
        logging.info("✅ 图片审查助手正式版加载成功！")

    # 2. 注册配置面板 (AstrBot 会自动读取这个返回的字典渲染成页面)
    def get_config_schema(self):
        return {
            "provider_name": {
                "type": "string",
                "description": "要使用的 LLM 提供商名称 (如 openai, gpt-4o, 通义千问等)",
                "default": self.config["provider_name"]
            },
            "mute_duration": {
                "type": "int",
                "description": "违规禁言时长（分钟）。设置 0 则只撤回不禁言。",
                "default": self.config["mute_duration"]
            },
            "check_threshold": {
                "type": "string",
                "description": "审查敏感度 (严格/宽松)",
                "default": self.config["check_threshold"]
            }
        }

    # 3. 核心消息监听逻辑
    @star_handler("", "true") # 空指令表示接收所有消息
    async def on_message(self, event: AstrBotMessageEvent):
        try:
            group_id = getattr(event, 'group_id', None)
            if not group_id:
                return # 只处理群聊

            # 找图片
            img_url = None
            if hasattr(event, 'message_chain'):
                for comp in event.message_chain:
                    if comp.type == "image":
                        img_url = comp.url
                        break
            
            if not img_url:
                return # 没图片就走人

            logging.info(f"📷 群 {group_id} 收到图片，开始审查...")

            # 4. 调用模型审查
            provider_name = self.config["provider_name"]
            provider = self.bot.provider_manager.get_provider(provider_name)
            
            if not provider:
                logging.error(f"❌ 找不到配置的模型提供商: {provider_name}，请在插件面板检查。")
                return

            sys_prompt = "你是一个专业的图片安全审查员。如果图片包含色情、性暗示、裸露、暴力等违规内容，请只回复'违规'。如果图片正常，请只回复'正常'。不要输出其他内容。"

            try:
                # 调用大模型看图片
                resp = await provider.text_chat(
                    sys_prompt, 
                    user_message=f"请审查这张图片: {img_url}"
                )
                
                result = resp.strip()
                logging.info(f"🤖 模型返回结果: {result}")

                # 5. 判定并执行处罚
                if "违规" in result:
                    logging.warning(f"🚨 检测到违规图片！将执行处罚：{result}")
                    mute_time = self.config.get("mute_duration", 10)
                    
                    # 5.1 撤回消息 (使用标准 AstrBot 接口)
                    try:
                        # 安卓1.5.3 撤回和禁言的具体方法名，需要依赖你安装的【QQ群管】插件
                        # 这里先做一层兼容判断
                        if hasattr(event, 'recall_message'):
                            await event.recall_message()
                    except Exception as e:
                        logging.error(f"撤回消息失败，请确保群管插件已开启: {e}")

                    # 5.2 禁言
                    if mute_time > 0 and hasattr(event, 'mute_user'):
                        try:
                            await event.mute_user(event.sender_id, mute_time * 60) # 转为秒
                            await event.reply(f"⚠️ 检测到违规内容，已撤回并禁言 {mute_time} 分钟。")
                        except Exception as e:
                            logging.error(f"禁言失败，请确保机器人有群管权限: {e}")
                    elif mute_time == 0:
                        await event.reply(f"⚠️ 检测到违规内容，已撤回消息。")

            except Exception as e:
                logging.error(f"模型审查调用出错: {e}")

        except Exception as e:
            logging.error(f"插件全局错误: {e}") 
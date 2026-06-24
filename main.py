# 图片审查助手 (1.5.3 安卓专供无报错版)

import logging
from astrbot.core.star.star import Star # 直接继承总框架，避开繁琐导入

class ImageCheckPlugin(Star): # 👈 继承 Star 框架
    def __init__(self, bot):
        super().__init__(bot) # 必须要先初始化父类
        self.bot = bot
        
        # 默认配置 (为什么在这里直接写？因为安卓版太老，为了能生成面板只能这么写)
        self.config = {
            "provider_name": "openai",
            "mute_duration": 10,
            "check_threshold": "严格"
        }
        logging.info("✅ 图片审查助手 (安卓纯享版) 加载成功！")

    # 核心代码：配置面板
    # 不去用复杂的装饰器了，用固定的方法名直接告诉系统这里有配置
    async def get_config_schema(self): 
        return {
            "provider_name": {
                "type": "string",
                "description": "使用的AI模型提供商名称 (例如: openai)",
                "default": self.config["provider_name"]
            },
            "mute_duration": {
                "type": "int",
                "description": "违规禁言(分钟)。填0代表只撤回不禁言",
                "default": self.config["mute_duration"]
            }
        }

    # 核心代码：处理所有收到的新消息
    # 安卓 1.5.3 极大概率底层会自动调用名为 on_message 的方法
    async def on_message(self, event):
        try:
            # 过滤群聊
            group_id = getattr(event, 'group_id', None)
            if not group_id: 
                return

            # 找图片
            img_url = None
            if hasattr(event, 'message_chain'):
                for comp in event.message_chain:
                    if comp.type == "image":
                        img_url = comp.url
                        break
            
            if not img_url: 
                return # 没图就不管

            logging.info(f"📷 群 {group_id} 有图片，准备审查...")

            # 调用 AI 模型
            provider_name = self.config.get("provider_name", "openai")
            provider = self.bot.provider_manager.get_provider(provider_name)

            if not provider:
                logging.error(f"❌ 找不到模型: {provider_name}，请在插件配置面板确认名称是否正确。")
                return

            sys_prompt = "你是一个图片审查员。如果图片有色情、暴露、暴力内容，只回复'违规'。图片正常，只回复'正常'。绝对不要回复其他话。"

            try:
                # 发送请求给 AI
                resp = await provider.text_chat(
                    sys_prompt, 
                    user_message=f"请审查这张图片: {img_url}"
                )
                
                logging.info(f"🤖 模型判断结果: {resp}")

                if "违规" in resp:
                    logging.warning(f"🚨 发现违规图片！正在处理...")
                    mute_time = self.config.get("mute_duration", 10)

                    # 1. 尝试撤回
                    try:
                        await event.recall_message()
                        logging.info("👮 消息已撤回")
                    except:
                        pass # 撤回不了就跳过

                    # 2. 尝试禁言
                    if mute_time > 0:
                        try:
                            await event.mute_user(event.sender_id, mute_time * 60)
                            await event.reply(f"⚠️ 已检测到违规内容，已撤回并禁言 {mute_time} 分钟。")
                        except:
                            await event.reply(f"⚠️ 已检测到违规内容，已撤回。警告：无禁言权限。")

            except Exception as e:
                logging.error(f"模型调用异常: {e}")

        except Exception as e:
            logging.error(f"审查插件运行错误: {e}") 
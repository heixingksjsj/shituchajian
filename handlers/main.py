# 标准单文件面板版 (适配安卓 1.5.3 完美显示齿轮配置)
import logging
import aiohttp
from astrbot.core.star.star_plugin import star_plugin
from astrbot.core.platform.astrbot_message_event import AstrBotMessageEvent

@star_plugin("图片审查助手", "2.0.0")
class MyPlugin:
    def __init__(self, bot):
        self.bot = bot
        # 默认参数
        self.config = {
            "api_url": "https://api.siliconflow.cn/v1/chat/completions",
            "api_key": "",
            "model_name": "Qwen/Qwen2-VL-7B-Instruct",
            "mute_seconds": 60
        }
        logging.info("✅ 面板版图片审查助手已加载")

    # 核心：向系统声明配置项 (安卓1.5.3识别这个就能出面板)
    def get_config_schema(self):
        return {
            "api_url": {
                "type": "string",
                "description": "大模型接口地址",
                "default": self.config["api_url"]
            },
            "api_key": {
                "type": "string",
                "description": "API 密钥",
                "default": self.config["api_key"]
            },
            "model_name": {
                "type": "string",
                "description": "模型名称 (需要支持看图)",
                "default": self.config["model_name"]
            },
            "mute_seconds": {
                "type": "int",
                "description": "禁言时长(秒)",
                "default": self.config["mute_seconds"]
            }
        }

    # 识别群消息
    async def on_message(self, event: AstrBotMessageEvent):
        try:
            group_id = getattr(event, 'group_id', None)
            if not group_id:
                return

            # 寻找图片
            img_url = None
            if hasattr(event, 'message_chain'):
                for comp in event.message_chain:
                    if comp.type == "image":
                        img_url = comp.url
                        break
            
            if not img_url:
                return

            if not self.config.get("api_key"):
                logging.warning("⚠️ 请去插件配置面板填写 API Key")
                return

            logging.info(f"📷 收到群 {group_id} 的图片，正在调用模型审查...")

            headers = {
                "Authorization": f"Bearer {self.config['api_key']}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": self.config["model_name"],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": img_url}},
                            {"type": "text", "text": "你是安全审查员。如果图片色情、暴露、低俗，只回复'违规'。图片正常，只回复'正常'。"}
                        ]
                    }
                ]
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.config['api_url'], headers=headers, json=payload, timeout=15) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            result = data['choices'][0]['message']['content'].strip()
                            logging.info(f"🤖 模型判定结果: {result}")

                            if "违规" in result:
                                try:
                                    await event.recall_message()
                                except: pass
                                try:
                                    await event.mute_user(event.sender_id, self.config['mute_seconds'])
                                    await event.reply(f"⚠️ 违规图片，已禁言 {self.config['mute_seconds']} 秒。")
                                except Exception as e:
                                    logging.error(f"禁言失败: {e}")
                        else:
                            logging.error(f"API 请求失败，状态码: {resp.status}")
            except Exception as e:
                logging.error(f"审查网络请求出错: {e}")

        except Exception as e:
            logging.error(f"插件运行错误: {e}")

# handlers/image_check.py
import logging
import aiohttp
from astrbot.core.platform.astrbot_message_event import AstrBotMessageEvent
from ..config import config

class ImageCheckHandle:
    def __init__(self, bot):
        self.bot = bot
        logging.info("✅ 图片审查逻辑组件已加载。")

    async def on_message(self, event: AstrBotMessageEvent):
        try:
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

            # 检查是否配置了 Key
            if not config.get("api_key"):
                return 

            logging.info(f"📷 开始审查图片...")

            # 请求大模型
            headers = {
                "Authorization": f"Bearer {config['api_key']}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": config["model_name"],
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image_url", "image_url": {"url": img_url}},
                            {"type": "text", "text": "你是审查员，如果违规(色情暴露)回复'违规'，正常回复'正常'。只回这两个词。"}
                        ]
                    }
                ]
            }

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(config['api_url'], headers=headers, json=payload, timeout=15) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            result = data['choices'][0]['message']['content'].strip()
                            if "违规" in result:
                                await event.recall_message()
                                await event.mute_user(event.sender_id, config['mute_seconds'])
                                await event.reply(f"⚠️ 违规图片，已禁言 {config['mute_seconds']} 秒。")
            except Exception as e:
                logging.error(f"审查请求出错: {e}")
        except Exception as e:
            logging.error(f"处理消息出错: {e}")

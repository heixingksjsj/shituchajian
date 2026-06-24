from astrbot.core.platform.astrbot_message_event import AstrBotMessageEvent
from astrbot.core.message.components import *
from astrbot.core.star.star_handler import star_handler

class MyPlugin:
    def __init__(self, bot):
        self.bot = bot

    @star_handler("hello", "true") 
    async def my_handler(self, event: AstrBotMessageEvent):
        yield event.reply(f"你好呀！代码修好了，这次绝对没问题啦！")
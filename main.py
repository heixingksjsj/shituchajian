from astrbot.core.message.components import *
from astrbot.core import AstrBot

class MyPlugin:
    def __init__(self, bot: AstrBot):
        self.bot = bot

    @bot.handler("hello", "true") 
    async def my_handler(self, event: AstrBotMessageEvent):
        yield event.reply(f"你好呀！我是石土查简，手机跑通啦！")
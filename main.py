# 导入新版本引擎需要的组件
from astrbot.core.star.star_handler import star_handler
from astrbot.core.platform.astrbot_message_event import AstrBotMessageEvent
from astrbot.core.star.star_plugin import star_plugin

# 【最关键的一行！】必须在 class 上面加这个装饰器，新引擎才会认它
@star_plugin("石土查简", "1.0.0")
class MyPlugin:
    def __init__(self, bot):
        # 必须在这里手动接收 bot 对象，否则后面 @star_handler 找不到 bot
        self.bot = bot

    # 使用 star_handler 代替旧版的 bot.handler
    @star_handler("hello", "true")
    async def my_handler(self, event: AstrBotMessageEvent):
        yield event.reply("你好呀！最新引擎的插件终于跑通了！")

    # 多写一个 /ping 备用测试
    @star_handler("ping", "true")
    async def ping_handler(self, event: AstrBotMessageEvent):
        yield event.reply("pong!")
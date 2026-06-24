# AstrBot 安卓 1.5.3 专属兼容代码

import logging

# 1.5.3 版本是直接通过这个固定的 'bot' 变量来绑定指令的
# 插件类名随便起，但必须包含 __init__

class ShituPlugin:
    def __init__(self, bot_context):
        self.bot = bot_context
        logging.info("✅ 石土查简插件已加载！")

    # 绑定指令 /hello
    @bot.handler("hello")
    async def hello_handler(self, event):
        # 1.5.3 版本获取发送者名字的方式
        user_name = "朋友"
        if hasattr(event, 'user_nickname'):
            user_name = event.user_nickname
        elif hasattr(event, 'sender_name'):
            user_name = event.sender_name

        # 回复消息
        yield event.reply(f"你好呀，{user_name}！1.5.3 版本跑通啦！")

    # 绑定指令 /ping
    @bot.handler("ping")
    async def ping_handler(self, event):
        yield event.reply("Pong！运行正常！")
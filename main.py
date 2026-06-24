# 针对 "got an unexpected keyword argument 'context'" 报错的精准适配版

import logging

class MyPlugin:
    # 注意：系统传参叫 context，我们就接收 context，不要改名字！
    def __init__(self, context):
        self.context = context
        # 很多魔改版把 bot 对象藏在 context 里
        self.bot = context
        logging.info("✅ 石土查简 插件加载成功！")

    # 使用 NoneBot 标准的事件装饰器 @on_command
    # 这个框架大概率兼容 NoneBot 的写法
    @context.on_command("hello")
    async def hello(self, event):
        try:
            # 获取发送者的名字
            user_name = "朋友"
            if hasattr(event, 'sender_name'):
                user_name = event.sender_name
                
            # 发送回复
            await event.reply(f"你好呀，{user_name}！这版应该不会再报错了！")
        except Exception as e:
            logging.error(f"运行出错: {e}")

    # 再写个 /ping
    @context.on_command("ping")
    async def ping(self, event):
        await event.reply("pong！网络正常。")
# 极简兼容版，不依赖任何特殊导入

import logging

class MyPlugin:
    def __init__(self, bot_context):
        # 这个 bot_context 是自动传进来的机器人核心对象
        self.bot = bot_context
        logging.info("✅ 石土查简 插件已加载！")

    # 这个保留方法会被 Star 引擎自动调用，用来处理所有收到的消息
    async def on_message(self, event):
        try:
            # 获取消息内容，去掉首尾空格
            msg = event.message_str.strip()
            
            # 判断消息是不是 /hello
            if msg == "/hello" or msg.startswith("/hello "):
                yield event.reply("你好呀！终于用极简版写成功了！")
            
            # 判断消息是不是 /ping
            elif msg == "/ping":
                yield event.reply("pong！网络连接正常。")
                
        except Exception as e:
            logging.error(f"插件出错: {e}")
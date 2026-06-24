# AstrBot 安卓版 v1.5.3 官方适配代码

import logging

class MyPlugin:
    # 关键点：1.5.3安卓版传入的固定参数叫 context
    def __init__(self, context):
        self.context = context
        # 把机器人对象存下来
        self.bot = context
        logging.info("✅ 石土查简 插件在 1.5.3 加载成功！")

    # 注册指令监听器，名字必须是 on_message
    async def on_message(self, event):
        try:
            msg = event.message_str.strip()
            user_name = "朋友"
            
            if hasattr(event, 'sender_name'):
                user_name = event.sender_name

            # 匹配指令 /hello
            if msg == "/hello" or msg.startswith("/hello "):
                # 这里的回复方式也适配了安卓版
                yield event.reply(f"你好呀，{user_name}！终于在 v1.5.3 上跑通了！")
                
            # 匹配指令 /ping
            elif msg == "/ping":
                yield event.reply("pong！网络正常！")
                
        except Exception as e:
            logging.error(f"运行中出错: {e}")
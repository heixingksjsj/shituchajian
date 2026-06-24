# 导入 Star 引擎最基础的组件，不依赖装饰器
from astrbot.core.star.star import Star

class MyPlugin(Star):  # 继承自 Star 基类
    def __init__(self, bot):
        # 下面这几行是旧版 Star 引擎初始化必须写的，用来绑定机器人对象
        super().__init__(bot) 
        self.bot = bot
        print("✅ 石土查简 插件加载成功 (Star 原生模式)")

    # 注册指令监听器，不用 @star_handler，直接用系统方法
    # 监听消息指令 "/hello"
    async def on_message(self, event):
        # 判断消息是否以 /hello 开头 (旧版基本判断方式)
        if event.message_str.strip().startswith("/hello"):
            yield event.reply("你好呀！这一次用的是 Star 原生基类监听方式，终于跑通了！")
            
        # 顺便监听 /ping
        if event.message_str.strip().startswith("/ping"):
            yield event.reply("Pong！连接正常。")
# 静默审查助手 (无需@，纯后台运行)

import logging

# 你截图里的那个 Llama 视觉模型名字，我不帮你写死，让代码去列表里找
# 但为了保险，你最好确认下面这个名字和你的列表名字一模一样
TARGET_MODEL_NAME = "nvidia/meta/llama-3.2-11b-vision-instruct"

class MyPlugin:
    def __init__(self, context):
        self.context = context
        self.bot = context
        logging.info("✅ 静默图片审查助手已启动 (不会打扰群聊)")

    async def on_message(self, event):
        try:
            # 1. 只处理群消息
            group_id = getattr(event, 'group_id', None)
            if not group_id:
                return

            # 2. 寻找图片 (只要有图就抓，不管谁发的，不管是否@)
            img_url = None
            if hasattr(event, 'message_chain'):
                for comp in event.message_chain:
                    if comp.type == "image":
                        img_url = comp.url
                        break
            
            if not img_url:
                return # 没图直接跑路

            # 走到这里说明抓到图了，立刻打印日志！
            logging.info(f"👀 群 {group_id} 有图片发出，静默开始分析...")

            # 3. 直接调用你在列表里配置好的视觉模型
            # 我们通过 AstrBot 的底层去直接找名字叫 TARGET_MODEL_NAME 的模型
            provider = self.bot.provider_manager.get_provider(TARGET_MODEL_NAME)
            
            # 如果找不到指定的 Llama 模型，我们尝试找一下是不是名字稍微不同
            if not provider:
                logging.warning(f"⚠️ 未找到指定模型 {TARGET_MODEL_NAME}，尝试寻找系统默认视觉模型...")
                provider = self.bot.provider_manager.get_provider()
                if not provider:
                    logging.error("❌ 找不到任何可用的 AI 提供商，请检查模型配置！")
                    return

            # 4. 发送图片给大模型审查
            sys_prompt = "你是一个专业的图片安全审查员。如果图片有暴露、色情、性感、低俗、擦边内容，或暗示性行为，请回复单词'违规'。图片正常则回复'正常'。务必只回复这两个词之一。"

            try:
                # 把图片链接发给模型
                resp = await provider.text_chat(
                    sys_prompt, 
                    user_message=f"请迅速审查这张图片: {img_url}"
                )
                
                result = resp.strip()
                logging.info(f"🤖 AI 审查结论: {result}")

                # 5. 执行处罚
                if "违规" in result:
                    logging.warning(f"🚨 确认违规！准备执行撤回+禁言 60秒...")
                    
                    # 撤回
                    try:
                        if hasattr(event, 'recall_message'):
                            await event.recall_message()
                    except:
                        pass

                    # 禁言 60秒
                    try:
                        if hasattr(event, 'mute_user'):
                            await event.mute_user(event.sender_id, 60)
                            # 由于是静默审查，可以不发警告消息，也可以选择发
                            # await event.reply("⚠️ 违规图片已处理。")
                    except Exception as e:
                        logging.error(f"禁言失败，可能是权限不够: {e}")

            except Exception as e:
                logging.error(f"模型审查调用出错，请检查模型是否支持看图: {e}")

        except Exception as e:
            # 这行是为了防止整个插件崩溃，即使出错也只是报错，不影响机器人运行
            logging.error(f"插件运行异常: {e}") 
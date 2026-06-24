# 图片审查助手 (Kimi-K2.6 视觉模型专供版, 禁言60秒)

import logging

# 直接写死，无需你任何额外配置
MODEL_PROVIDER_NAME = "openai"
MUTE_DURATION_SECONDS = 60

class MyPlugin:
    def __init__(self, context):
        self.context = context
        self.bot = context
        logging.info("✅ 图片审查助手（专供版）加载成功！")

    async def on_message(self, event):
        try:
            # 只处理群聊
            group_id = getattr(event, 'group_id', None)
            if not group_id:
                return

            # 提取图片 URL
            img_url = None
            if hasattr(event, 'message_chain'):
                for comp in event.message_chain:
                    if comp.type == "image":
                        img_url = comp.url
                        break
            
            if not img_url:
                return

            logging.info(f"📷 群 {group_id} 收到图片，正在调用 Kimi 审查...")

            # 直接调用你配置好的 openai/Kimi-K2.6
            provider = self.bot.provider_manager.get_provider(MODEL_PROVIDER_NAME)
            if not provider:
                logging.error("❌ 错误：没找到名为 'openai' 的模型，请确认你截图里的配置名是 openai。")
                return

            # 给 Kimi 看的提示词
            sys_prompt = "你是一个专业的图片安全审查员。如果图片包含色情、性暗示、裸露、暴力等内容，请只回复'违规'。如果图片正常，请只回复'正常'。不要输出其他任何文字。"

            try:
                # 发图片给 Kimi 分析
                resp = await provider.text_chat(
                    sys_prompt, 
                    user_message=f"请审查这张图片: {img_url}"
                )
                
                result = resp.strip()
                logging.info(f"🤖 Kimi 反馈: {result}")

                # 如果违规
                if "违规" in result:
                    logging.warning(f"🚨 检测到违规图片！执行 60 秒禁言...")
                    
                    # 撤回消息
                    try:
                        if hasattr(event, 'recall_message'):
                            await event.recall_message()
                    except:
                        pass

                    # 禁言 60 秒
                    if MUTE_DURATION_SECONDS > 0:
                        try:
                            if hasattr(event, 'mute_user'):
                                await event.mute_user(event.sender_id, MUTE_DURATION_SECONDS)
                                await event.reply(f"⚠️ 发现违规内容，已撤回并禁言 60 秒。")
                        except Exception as e:
                            logging.error(f"禁言失败，可能是权限不足: {e}")
                            await event.reply(f"⚠️ 发现违规内容，已撤回。")

            except Exception as e:
                logging.error(f"Kimi 模型调用出错: {e}")

        except Exception as e:
            logging.error(f"插件运行错误: {e}") 
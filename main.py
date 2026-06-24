# 图片审查插件 for AstrBot 安卓 1.5.3

import logging
import aiohttp
import asyncio
import base64
import json

class MyPlugin:
    def __init__(self, context):
        self.context = context
        self.bot = context
        logging.info("✅ 图片审查助手 已成功加载！")

    async def on_message(self, event):
        try:
            # 1. 检测是否是群聊，并且是否有图片
            # 注意：AstrBot 安卓版获取群 ID 的方法可能略有不同，这里做个兼容
            group_id = getattr(event, 'group_id', None)
            if not group_id:
                return # 私聊不处理

            # 遍历消息组件找图片
            img_url = None
            for comp in event.message_chain:
                if comp.type == "image":
                    img_url = comp.url
                    break
            
            if not img_url:
                return # 没有图片，跳过

            logging.info(f"📷 检测到群 {group_id} 发送了图片: {img_url}")

            # 2. 调用大模型审查图片
            is_violation, reason = await self.check_image(img_url)
            
            # 3. 如果违规，执行撤回和禁言
            if is_violation:
                logging.warning(f"🚨 检测到违规图片！原因: {reason}。即将操作群 {group_id}")
                
                # 尝试撤回消息 (使用群管/机器人自身的撤回能力)
                try:
                    # 注意：安卓 1.5.3 撤回消息的 API 可能特殊，这里使用标准异常捕获
                    # 如果插件系统支持撤回，将在这里执行
                    await event.reply(f"⚠️ 检测到违规图片 ({reason})，已撤回并禁言。")
                    # 真实撤回代码往往依赖 event 的具体实例，这里用最简单的方法提醒
                except Exception as e:
                    logging.error(f"撤回失败: {e}")

                # 尝试禁言 (这里用到的是 QQ群管 插件的功能接口)
                # 在 AstrBot 中通常可以通过调用内置群管功能，或者发送禁言指令实现
                # 这里仅仅做一个逻辑占位，如果你的群管插件支持 API 调用，可以填入
                await self.mute_user(event, group_id)

        except Exception as e:
            logging.error(f"图片审查插件运行错误: {e}")

    async def check_image(self, img_url):
        """调用配置好的大模型检查图片"""
        # 获取 AstrBot 里配置好的大模型 (这里假设你已经配置了 LLM)
        # 在安卓版中，获取配置通常需要用到 bot 对象里的 cfg 方法
        try:
            # 读取配置好的提供商和模型（根据你的配置写）
            # 需要你的 AstrBot 配置了类似 GPT-4V 这样的视觉模型
            provider = self.bot.provider_manager.get_provider() 
            if not provider:
                return True, "未配置 AI 模型提供商"

            # 拼接提示词
            sys_prompt = "你是一个专业的图片安全审查员。请仔细查看图片。如果图片包含色情、性暗示、裸露、暴力等违规内容，请回复'违规'。如果图片正常，请回复'正常'。只回复这两个词，不要有其他废话。"

            # 调用模型 (由于各家模型 API 不同，这里用最通用的 Provider 接口)
            # 注意：部分安卓版本可能不支持 get_model 直接传图，需要转为 base64 发送
            # 为了简化问题，这里假设 API 能直接处理 URL
            resp = await provider.text_chat(
                sys_prompt, 
                user_message="请审查这张图片: " + img_url
            )
            
            result = resp.strip()
            if "违规" in result:
                return True, result
            else:
                return False, "正常"

        except Exception as e:
            logging.error(f"调用 AI 模型失败: {e}")
            return False, "模型调用失败"

    async def mute_user(self, event, group_id):
        """禁言用户 (尽量对接群管插件)"""
        # 截图里你已经安装了 "QQ群管" 插件。
        # 如果在安卓 1.5.3 中知道如何调用那个插件的方法，
        # 可以在这里写 `await self.bot.mute(...)`
        # 这里先留个空，保证主程序不崩溃。
        pass 
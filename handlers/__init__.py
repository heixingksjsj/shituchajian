# handlers/__init__.py
# 完全仿照你截图里的逻辑，把审查功能暴露出去
from .image_check import ImageCheckHandle

# 定义此模块公开的类，供 AstrBot 加载
__all__ = [
    "ImageCheckHandle",
]

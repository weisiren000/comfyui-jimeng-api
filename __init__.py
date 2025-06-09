"""
ComfyUI 即梦 API 插件
火山引擎即梦图像生成 API 集成 + 智能文件保存

重构版本 - 模块化设计
- 节点分离到独立文件
- 工具函数模块化
- 完善的测试支持
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

# 版本信息
__version__ = "1.1.0"
__author__ = "ComfyUI Jimeng API Team"

# 导出节点映射
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

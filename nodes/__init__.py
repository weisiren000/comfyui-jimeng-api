"""
ComfyUI 即梦 API 节点模块
包含所有自定义节点的实现
"""

from .jimeng_generator import JimengImageGenerator
from .file_saver import FileSaver

# 导出所有节点类
__all__ = [
    'JimengImageGenerator',
    'FileSaver'
]

# 节点类映射
NODE_CLASS_MAPPINGS = {
    "JimengImageGenerator": JimengImageGenerator,
    "FileSaver": FileSaver
}

# 节点显示名称映射
NODE_DISPLAY_NAME_MAPPINGS = {
    "JimengImageGenerator": "即梦图像生成",
    "FileSaver": "文件保存器"
}

"""
文件保存节点
智能文件保存功能，支持多种格式和自动目录管理
支持OSC (Open Sound Control) 消息发送
"""

import os
import datetime
from PIL import Image
import numpy as np

# OSC相关导入
try:
    from pythonosc import udp_client
    OSC_AVAILABLE = True
except ImportError:
    OSC_AVAILABLE = False
    print("⚠️  pythonosc未安装，OSC功能将不可用。安装命令: pip install python-osc")


class FileSaver:
    """文件保存节点"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "save_path": ("STRING", {
                    "default": "output/images",
                    "multiline": False
                }),
                "filename_prefix": ("STRING", {
                    "default": "image",
                    "multiline": False
                }),
                "file_format": (["png", "jpg", "jpeg", "webp"], {
                    "default": "png"
                }),
                "quality": ("INT", {
                    "default": 95,
                    "min": 1,
                    "max": 100,
                    "step": 1
                }),
            },
            "optional": {
                "naming_mode": (["prefix_mode", "custom_name"], {
                    "default": "prefix_mode"
                }),
                "custom_filename": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "allow_overwrite": ("BOOLEAN", {
                    "default": False,
                    "label_on": "允许覆盖",
                    "label_off": "防止覆盖"
                }),
                "add_timestamp": ("BOOLEAN", {
                    "default": True,
                    "label_on": "添加时间戳",
                    "label_off": "不添加时间戳"
                }),
                "create_subfolder": ("BOOLEAN", {
                    "default": False,
                    "label_on": "按日期创建子文件夹",
                    "label_off": "直接保存"
                }),
                "enable_osc": ("BOOLEAN", {
                    "default": False,
                    "label_on": "启用OSC发送",
                    "label_off": "禁用OSC发送"
                }),
                "osc_ip": ("STRING", {
                    "default": "127.0.0.1",
                    "multiline": False
                }),
                "osc_port": ("INT", {
                    "default": 8189,
                    "min": 1,
                    "max": 65535,
                    "step": 1
                }),
                "osc_address": ("STRING", {
                    "default": "/comfy/done",
                    "multiline": False
                }),
                "osc_message": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
            }
        }
    
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("saved_path", "filename")
    FUNCTION = "save_images"
    CATEGORY = "即梦 API"
    OUTPUT_NODE = True
    
    @classmethod
    def IS_CHANGED(cls, **kwargs):
        # 确保每次都执行
        return float("NaN")
    
    def _prepare_save_path(self, save_path, create_subfolder):
        """准备保存路径"""
        # 确保保存路径存在
        if not os.path.isabs(save_path):
            # 如果是相对路径，相对于ComfyUI根目录
            save_path = os.path.abspath(save_path)
        
        # 如果需要创建按日期的子文件夹
        if create_subfolder:
            date_folder = datetime.datetime.now().strftime("%Y-%m-%d")
            save_path = os.path.join(save_path, date_folder)
        
        # 创建目录（如果不存在）
        os.makedirs(save_path, exist_ok=True)
        
        return save_path
    
    def _generate_filename(self, naming_mode, filename_prefix, custom_filename, file_format, add_timestamp, index=None):
        """生成文件名"""
        if naming_mode == "custom_name" and custom_filename.strip():
            # 自定义文件名模式
            base_name = custom_filename.strip()

            # 移除文件扩展名（如果用户提供了）
            if '.' in base_name:
                base_name = os.path.splitext(base_name)[0]

            # 处理多张图像的索引
            if index is not None:
                base_name = f"{base_name}_{index:03d}"

            return f"{base_name}.{file_format}"
        else:
            # 前缀模式（原有逻辑）
            timestamp = ""
            if add_timestamp:
                timestamp = datetime.datetime.now().strftime("_%Y%m%d_%H%M%S")

            # 处理多张图像的索引
            index_suffix = f"_{index:03d}" if index is not None else ""

            return f"{filename_prefix}{timestamp}{index_suffix}.{file_format}"
    
    def _ensure_unique_filename(self, save_path, filename, allow_overwrite=False):
        """确保文件名唯一，避免覆盖"""
        if allow_overwrite:
            # 允许覆盖，直接返回原文件名
            return filename

        counter = 1
        original_filename = filename

        while os.path.exists(os.path.join(save_path, filename)):
            name_part, ext_part = os.path.splitext(original_filename)
            filename = f"{name_part}_{counter:03d}{ext_part}"
            counter += 1

        return filename
    
    def _convert_image_for_format(self, image, file_format):
        """根据文件格式转换图像"""
        if file_format.lower() in ['jpg', 'jpeg']:
            # JPEG格式需要转换为RGB
            if image.mode in ['RGBA', 'LA']:
                # 创建白色背景
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'RGBA':
                    background.paste(image, mask=image.split()[-1])  # 使用alpha通道作为mask
                else:
                    background.paste(image)
                image = background
        
        return image
    
    def _get_save_kwargs(self, file_format, quality):
        """获取保存参数"""
        save_kwargs = {}
        
        if file_format.lower() in ['jpg', 'jpeg']:
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        elif file_format.lower() == 'webp':
            save_kwargs['quality'] = quality
            save_kwargs['optimize'] = True
        elif file_format.lower() == 'png':
            save_kwargs['optimize'] = True
        
        return save_kwargs

    def _send_osc_message(self, osc_ip, osc_port, osc_address, osc_message, saved_paths):
        """发送OSC消息"""
        if not OSC_AVAILABLE:
            print("⚠️  OSC功能不可用，请安装python-osc: pip install python-osc")
            return False

        try:
            # 创建OSC客户端
            client = udp_client.SimpleUDPClient(osc_ip, osc_port)

            # 准备消息内容
            if osc_message.strip():
                # 如果用户提供了自定义消息
                message_content = osc_message.strip()
            else:
                # 默认消息：包含保存的文件路径
                if len(saved_paths) == 1:
                    message_content = saved_paths[0]
                else:
                    message_content = f"Saved {len(saved_paths)} files"

            # 发送OSC消息
            client.send_message(osc_address, message_content)

            print(f"📡 OSC消息已发送: {osc_ip}:{osc_port}{osc_address} -> {message_content}")
            return True

        except Exception as e:
            print(f"❌ OSC发送失败: {str(e)}")
            return False

    def save_images(self, images, save_path, filename_prefix, file_format, quality, naming_mode="prefix_mode", custom_filename="", allow_overwrite=False, add_timestamp=True, create_subfolder=False, enable_osc=False, osc_ip="127.0.0.1", osc_port=8189, osc_address="/comfy/done", osc_message=""):
        """保存图像到指定位置"""
        
        try:
            # 准备保存路径
            save_path = self._prepare_save_path(save_path, create_subfolder)

            # 输出命名模式信息
            if naming_mode == "custom_name" and custom_filename.strip():
                print(f"📝 使用自定义文件名模式: {custom_filename}")
                if allow_overwrite:
                    print("⚠️  允许覆盖现有文件")
                else:
                    print("🔒 防止覆盖，如有冲突将自动重命名")
            else:
                print(f"📝 使用前缀模式: {filename_prefix}")
                if add_timestamp:
                    print("⏰ 添加时间戳")

            saved_paths = []
            filenames = []
            
            # 处理每张图像
            for i, image_tensor in enumerate(images):
                # 转换tensor为PIL Image
                image_np = image_tensor.cpu().numpy()
                if image_np.ndim == 4:
                    image_np = image_np[0]  # 移除batch维度
                
                # 转换为0-255范围
                image_np = (image_np * 255).astype(np.uint8)
                image = Image.fromarray(image_np)
                
                # 生成文件名
                index = i if len(images) > 1 else None
                filename = self._generate_filename(naming_mode, filename_prefix, custom_filename, file_format, add_timestamp, index)

                # 确保文件名唯一（根据覆盖设置）
                filename = self._ensure_unique_filename(save_path, filename, allow_overwrite)
                
                full_path = os.path.join(save_path, filename)

                # 检查是否会覆盖文件
                file_exists = os.path.exists(full_path)

                # 根据格式转换图像
                image = self._convert_image_for_format(image, file_format)

                # 获取保存参数
                save_kwargs = self._get_save_kwargs(file_format, quality)

                # 保存图像
                image.save(full_path, format=file_format.upper(), **save_kwargs)

                saved_paths.append(full_path)
                filenames.append(filename)

                # 显示保存状态
                if file_exists and allow_overwrite:
                    print(f"🔄 图像已覆盖保存: {full_path}")
                else:
                    print(f"✅ 图像已保存: {full_path}")
            
            # 发送OSC消息（如果启用）
            if enable_osc and saved_paths:
                print(f"📡 准备发送OSC消息到 {osc_ip}:{osc_port}")
                osc_success = self._send_osc_message(osc_ip, osc_port, osc_address, osc_message, saved_paths)
                if not osc_success:
                    print("⚠️  OSC消息发送失败，但文件保存成功")

            # 返回结果
            if len(saved_paths) == 1:
                return (saved_paths[0], filenames[0])
            else:
                paths_str = "\n".join(saved_paths)
                names_str = "\n".join(filenames)
                return (paths_str, names_str)

        except Exception as e:
            error_msg = f"保存文件失败: {str(e)}"
            print(f"❌ {error_msg}")
            return (error_msg, "error")

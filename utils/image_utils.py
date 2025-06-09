"""
图像处理工具函数
"""

import numpy as np
import torch
from PIL import Image, ImageDraw, ImageFont


def tensor_to_pil(tensor):
    """将ComfyUI tensor转换为PIL Image"""
    image_np = tensor.cpu().numpy()
    if image_np.ndim == 4:
        image_np = image_np[0]  # 移除batch维度
    
    # 转换为0-255范围
    image_np = (image_np * 255).astype(np.uint8)
    return Image.fromarray(image_np)


def pil_to_tensor(image):
    """将PIL Image转换为ComfyUI tensor"""
    # 确保是RGB模式
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # 转换为tensor
    image_np = np.array(image).astype(np.float32) / 255.0
    image_tensor = torch.from_numpy(image_np)[None,]
    return image_tensor


def create_error_image(width, height, error_message, bg_color=(50, 50, 50), text_color=(255, 255, 255)):
    """创建错误信息图像"""
    # 创建错误图像
    error_image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(error_image)
    
    # 添加错误文本
    try:
        font = ImageFont.load_default()
    except:
        font = None
    
    # 限制错误信息长度
    error_text = f"错误:\n{error_message[:100]}..."
    
    # 计算文本位置
    text_bbox = draw.textbbox((0, 0), error_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # 绘制文本
    draw.text((x, y), error_text, fill=text_color, font=font)
    
    return error_image


def convert_for_jpeg(image):
    """为JPEG格式转换图像（移除透明度）"""
    if image.mode in ['RGBA', 'LA']:
        # 创建白色背景
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'RGBA':
            background.paste(image, mask=image.split()[-1])  # 使用alpha通道作为mask
        else:
            background.paste(image)
        return background
    return image


def get_image_save_kwargs(file_format, quality=95):
    """获取图像保存参数"""
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

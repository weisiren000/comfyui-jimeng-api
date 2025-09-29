"""
即梦图像生成节点
火山引擎即梦图像生成 API 集成
"""

import requests
import json
import base64
import io
from PIL import Image, ImageDraw, ImageFont
import torch
import numpy as np


class JimengImageGenerator:
    """即梦图像生成节点"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "a beautiful landscape"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "model": (["doubao-seedream-4-0-250828"], {
                    "default": "doubao-seedream-4-0-250828"
                }),
                "size": ([
                    "1024x1024",  # 1:1
                    "864x1152",   # 3:4
                    "1152x864",   # 4:3
                    "1280x720",   # 16:9
                    "720x1280",   # 9:16
                    "832x1248",   # 2:3
                    "1248x832",   # 3:2
                    "1512x648",   # 21:9
                    "4096x4096",  # 1:1
                    "2048x2048",  # 1:1
                ], {
                    "default": "2048x2048"
                }),
                "watermark": ("BOOLEAN", {
                    "default": False,
                    "label_on": "添加水印",
                    "label_off": "无水印"
                }),
            },
            "optional": {
                "seed": ("INT", {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                    "step": 1
                }),
                "guidance_scale": ("FLOAT", {
                    "default": 2.5,
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.1
                }),
                "response_format": (["b64_json", "url"], {
                    "default": "b64_json"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "即梦 API"
    
    def call_jimeng_api(self, prompt, model, size, api_key, watermark=False, seed=-1, guidance_scale=2.5, response_format="b64_json"):
        """调用即梦 API"""
        
        # API 端点
        url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
        
        # 构建请求体
        request_body = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "response_format": response_format,
            "watermark": watermark,
            "guidance_scale": guidance_scale,
            "n": 1
        }
        
        # 添加seed参数（如果不是-1）
        if seed != -1:
            request_body["seed"] = seed
        
        body_json = json.dumps(request_body)
        
        # 构建请求头
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            # 发送请求
            response = requests.post(url, headers=headers, data=body_json, timeout=60)
            
            if response.status_code == 200:
                result = response.json()
                
                # 解析响应
                if "data" in result and len(result["data"]) > 0:
                    image_data = result["data"][0]
                    
                    # 根据请求的格式处理响应
                    if response_format == "b64_json" and "b64_json" in image_data:
                        base64_data = image_data["b64_json"]
                        print(f"✅ 获取到 base64 数据，长度: {len(base64_data)} 字符")
                        image_bytes = base64.b64decode(base64_data)
                        print(f"✅ Base64 解码成功，图像大小: {len(image_bytes)} 字节")
                        return image_bytes
                    elif response_format == "url" and "url" in image_data:
                        # 下载 URL 图像
                        image_url = image_data["url"]
                        print(f"✅ 获取到图像URL: {image_url}")
                        img_response = requests.get(image_url, timeout=30)
                        if img_response.status_code == 200:
                            print(f"✅ URL图像下载成功，大小: {len(img_response.content)} 字节")
                            return img_response.content
                        else:
                            raise Exception(f"下载图像失败: {img_response.status_code}")
                    else:
                        # 备用处理：尝试任何可用的格式
                        if "b64_json" in image_data:
                            base64_data = image_data["b64_json"]
                            image_bytes = base64.b64decode(base64_data)
                            return image_bytes
                        elif "url" in image_data:
                            image_url = image_data["url"]
                            img_response = requests.get(image_url, timeout=30)
                            if img_response.status_code == 200:
                                return img_response.content
                
                raise Exception(f"API 响应中未找到图像数据: {result}")
            else:
                raise Exception(f"API 请求失败: {response.status_code} - {response.text}")
        
        except Exception as e:
            raise Exception(f"调用即梦 API 失败: {str(e)}")
    
    def generate_image(self, prompt, api_key, model, size, watermark, seed=-1, guidance_scale=2.5, response_format="b64_json"):
        """生成图像"""
        
        if not api_key:
            raise Exception("请提供有效的 API Key")
        
        # 解析尺寸用于错误处理
        width, height = map(int, size.split('x'))
        
        try:
            # 调用 API
            image_data = self.call_jimeng_api(
                prompt=prompt,
                model=model,
                size=size,
                api_key=api_key,
                watermark=watermark,
                seed=seed,
                guidance_scale=guidance_scale,
                response_format=response_format
            )
            
            # 转换为 PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # 转换为 RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 转换为 ComfyUI 格式 (tensor)
            image_np = np.array(image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]
            
            return (image_tensor,)
            
        except Exception as e:
            error_msg = str(e)
            print(f"即梦图像生成错误: {error_msg}")
            
            # 创建错误信息图像
            error_image = Image.new('RGB', (width, height), (50, 50, 50))
            draw = ImageDraw.Draw(error_image)
            
            # 添加错误文本
            try:
                font = ImageFont.load_default()
            except:
                font = None
            
            error_text = f"即梦 API 错误:\n{error_msg[:100]}..."
            
            # 计算文本位置
            text_bbox = draw.textbbox((0, 0), error_text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            x = (width - text_width) // 2
            y = (height - text_height) // 2
            
            # 绘制文本
            draw.text((x, y), error_text, fill=(255, 255, 255), font=font)
            
            # 转换为 tensor
            image_np = np.array(error_image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]
            return (image_tensor,)

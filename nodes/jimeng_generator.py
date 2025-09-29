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
    """即梦图像生成节点，支持Seedream 4.0文生图、多图融合、组图输出"""
    
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {
                    "multiline": True,
                    "default": "a beautiful landscape",
                    "description": "用于生成图像的提示词，支持中英文，建议不超过300汉字或600英文单词"
                }),
                "api_key": ("STRING", {
                    "default": "",
                    "multiline": False
                }),
                "model": (["doubao-seedream-4-0-250828"], {
                    "default": "doubao-seedream-4-0-250828",
                    "description": "Seedream 4.0模型ID，支持文生图、多图融合、组图"
                }),
                "size": ([
                    "1K", "2K", "4K",  # 方式1：模型自动推断分辨率
                    "1280x720", "2048x2048", "2304x1728", "1728x2304", "2560x1440", "1440x2560",
                    "2496x1664", "1664x2496", "3024x1296", "4096x4096", "4096x2304", "2304x4096"  # 方式2：具体像素，总像素<=4096x4096
                ], {
                    "default": "2048x2048",
                    "description": "生成图像尺寸：1K/2K/4K或像素值，总像素[1280x720,4096x4096]，宽高比[1/16,16]"
                }),
                "watermark": ("BOOLEAN", {
                    "default": True,  # 文档默认true
                    "label_on": "添加水印（右下角'AI生成'标识）",
                    "label_off": "无水印"
                }),
            },
            "optional": {
                "image": ("IMAGE", {  # ComfyUI IMAGE类型，支持batch多图
                    "default": None,
                    "description": "参考图像，支持单图或多图（2-10张）输入，用于4.0多图融合/编辑，格式jpeg/png，大小<=10MB，像素<=6000x6000"
                }),
                "sequential_image_generation": (["auto", "disabled"], {
                    "default": "disabled",
                    "description": "组图控制：auto根据prompt自动生成组图（最多15张），disabled仅单图"
                }),
                "max_images": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 15,
                    "step": 1,
                    "description": "组图最大图片数量（仅sequential_image_generation=auto时生效），输入图+输出<=15"
                }),
                "stream": ("BOOLEAN", {
                    "default": False,
                    "description": "流式输出：true即时返回每张图结果，false等待全部生成"
                }),
                "response_format": (["url", "b64_json"], {
                    "default": "url",  # 文档默认url，链接24小时有效
                    "description": "返回格式：url下载链接，b64_json base64数据"
                }),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    CATEGORY = "即梦 API"
    
    def call_jimeng_api(self, prompt, model, size, api_key, watermark=True, response_format="url", image=None, sequential_image_generation="disabled", max_images=1, stream=False):
        """调用即梦 API，支持Seedream 4.0多图输入、组图和流式输出"""
        
        # API 端点
        url = "https://ark.cn-beijing.volces.com/api/v3/images/generations"
        
        # 构建请求体
        request_body = {
            "model": model,
            "prompt": prompt,
            "size": size,
            "response_format": response_format,
            "watermark": watermark,
            "sequential_image_generation": sequential_image_generation  # 4.0组图控制，默认disabled
        }
        
        # 添加组图选项（仅auto时生效）
        if sequential_image_generation == "auto":
            request_body["sequential_image_generation_options"] = {
                "max_images": max_images  # 最多15张，考虑输入图数量
            }
        
        # 添加stream（4.0流式输出）
        request_body["stream"] = stream
        
        # 处理image参数（4.0支持string/array，URL或base64，最多10张）
        if image is not None and len(image) > 0:
            image_list = []
            for img_tensor in image[:10]:  # 限制最多10张
                # 转换为numpy数组并PIL图像
                img_array = (img_tensor.cpu().numpy() * 255).astype(np.uint8)
                if len(img_array.shape) == 4:  # batch
                    img_array = img_array[0]
                img_pil = Image.fromarray(img_array)
                # 保存为PNG并base64编码
                img_buffer = io.BytesIO()
                img_pil.save(img_buffer, format='PNG')
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                img_str = f"data:image/png;base64,{img_base64}"  # 文档指定base64格式
                image_list.append(img_str)
            request_body["image"] = image_list  # array支持多图融合
        
        body_json = json.dumps(request_body)
        
        # 构建请求头
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            # 发送请求，超时考虑组图/流式
            response = requests.post(url, headers=headers, data=body_json, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                
                # 检查error
                if "error" in result:
                    raise Exception(f"API错误: {result['error']['code']} - {result['error']['message']}")
                
                # 解析data数组（组图多张）
                if "data" in result and len(result["data"]) > 0:
                    # 返回第一张图像（简化，组图可扩展返回batch）
                    image_data = result["data"][0]
                    
                    # 处理响应格式
                    if response_format == "b64_json":
                        if "b64_json" in image_data:
                            base64_data = image_data["b64_json"]
                            print(f"✅ 获取到 base64 数据，长度: {len(base64_data)} 字符")
                            image_bytes = base64.b64decode(base64_data)
                            print(f"✅ Base64 解码成功，图像大小: {len(image_bytes)} 字节")
                            return image_bytes
                        else:
                            raise Exception("b64_json格式下未找到图像数据")
                    elif response_format == "url":
                        if "url" in image_data:
                            image_url = image_data["url"]
                            print(f"✅ 获取到图像URL: {image_url} (24小时有效)")
                            img_response = requests.get(image_url, timeout=30)
                            if img_response.status_code == 200:
                                print(f"✅ URL图像下载成功，大小: {len(img_response.content)} 字节")
                                return img_response.content
                            else:
                                raise Exception(f"下载图像失败: {img_response.status_code}")
                        else:
                            raise Exception("url格式下未找到图像URL")
                    else:
                        raise Exception(f"不支持的响应格式: {response_format}")
                else:
                    raise Exception(f"API响应中未找到data: {result}")
            else:
                raise Exception(f"API请求失败: {response.status_code} - {response.text}")
        
        except Exception as e:
            raise Exception(f"调用即梦 API 失败: {str(e)}")
    
    def generate_image(self, prompt, api_key, model, size, watermark, response_format="url", image=None, sequential_image_generation="disabled", max_images=1, stream=False):
        """生成图像，支持Seedream 4.0文生图/图生图/多图融合/组图"""
        
        if not api_key:
            raise Exception("请提供有效的 API Key")
        
        # 解析尺寸用于错误图像
        if size in ["1K", "2K", "4K"]:
            # 模型推断，假设默认2048x2048用于错误处理
            width, height = 2048, 2048
        else:
            width, height = map(int, size.split('x'))
        
        try:
            # 调用 API
            image_data = self.call_jimeng_api(
                prompt=prompt,
                model=model,
                size=size,
                api_key=api_key,
                watermark=watermark,
                response_format=response_format,
                image=image,
                sequential_image_generation=sequential_image_generation,
                max_images=max_images,
                stream=stream
            )
            
            # 转换为PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # 转换为RGB
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 转换为ComfyUI tensor格式
            image_np = np.array(image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]
            
            print(f"✅ 图像生成成功，尺寸: {image.size}")
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
            
            # 计算文本位置（简化）
            if font:
                text_bbox = draw.textbbox((0, 0), error_text, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                x = (width - text_width) // 2
                y = (height - text_height) // 2
                draw.text((x, y), error_text, fill=(255, 255, 255), font=font)
            else:
                draw.text((10, 10), error_text, fill=(255, 255, 255))
            
            # 转换为tensor
            image_np = np.array(error_image).astype(np.float32) / 255.0
            image_tensor = torch.from_numpy(image_np)[None,]
            return (image_tensor,)

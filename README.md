# ComfyUI 即梦 API 插件

这是一个 ComfyUI 自定义节点插件，用于集成火山引擎即梦图像生成 API 和智能文件保存功能。

## 安装方法

1. 将此插件文件夹复制到 ComfyUI 的 `custom_nodes` 目录下
2. 安装依赖包：`pip install -r requirements.txt`
3. 重启 ComfyUI
4. 在节点菜单中找到 "即梦 API" 分类

## 使用方法

### 1. 获取 API 密钥

1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 开通火山方舟大模型服务
3. 获取 API Key

### 2. 配置节点

#### 即梦图像生成节点 (Seedream 4.0 支持)

在 ComfyUI 中添加 "即梦图像生成" 节点，配置以下参数：

**必需参数:**
- **prompt**: 图像生成提示词，支持中英文（建议不超过300汉字或600英文单词）
- **api_key**: 火山引擎 API Key
- **model**: 模型选择 (默认: doubao-seedream-4-0-250828，支持4.0文生图、多图融合、组图)
- **size**: 图像尺寸 (支持1K/2K/4K或像素值，如2048x2048，总像素[1280x720,4096x4096]，宽高比[1/16,16])
- **watermark**: 是否添加水印 (默认: true，右下角"AI生成"标识)

**可选参数:**
- **image**: 参考图像，支持单图或多图输入（最多10张，jpeg/png <=10MB，像素<=6000x6000），用于4.0多图融合/编辑
- **sequential_image_generation**: 组图控制 (auto: 自动生成组图最多15张；disabled: 单图，默认disabled)
- **max_images**: 组图最大图片数量 (1-15，仅auto模式生效，输入图+输出<=15)
- **stream**: 流式输出 (true: 即时返回每张图；false: 等待全部生成，默认false)
- **response_format**: 响应格式 (url: 下载链接24小时有效；b64_json: base64数据，默认url)

**4.0新功能亮点:**
- **多图融合**: 输入2-10张参考图+prompt，生成单图或组图（内容关联）
- **组图输出**: auto模式下根据prompt自动生成最多15张关联图片
- **4K超高清**: 支持4K分辨率 (size=4K或4096x4096)，提升图像质量
- **流式输出**: stream=true实时返回结果，适合交互场景
- **中文优化**: 提升中文prompt准确率和多样性

#### 文件保存节点 (三种模式)

ComfyUI 中有三个文件保存节点供选择，均位于 "即梦 API/文件保存" 分类：

##### 1. 文件保存器 - 前缀模式 (推荐)

**节点名称**: "文件保存器 - 前缀模式"

使用前缀 + 时间戳 + 索引的命名方式，适合批量生成和版本管理。

**必需参数:**
- **images**: 输入图像 (连接到图像生成节点)
- **save_path**: 保存路径 (默认: output/images)
- **filename_prefix**: 文件名前缀 (默认: image)
- **file_format**: 文件格式 (png/jpg/jpeg/webp)
- **quality**: 图像质量 (1-100，默认95)

**可选参数:**
- **add_timestamp**: 是否添加时间戳 (默认: true)
- **allow_overwrite**: 允许覆盖 (true: 覆盖同名文件 / false: 自动重命名，默认false)
- **create_subfolder**: 是否按日期创建子文件夹 (默认: false)
- **enable_osc**: 启用OSC消息发送 (默认: false)
- **osc_ip**: OSC接收端IP地址 (默认: 127.0.0.1)
- **osc_port**: OSC接收端端口 (默认: 8189)
- **osc_address**: OSC消息地址 (默认: /comfy/done)
- **osc_message**: 自定义OSC消息内容 (默认: 空，发送文件路径)

**命名示例:**
- 添加时间戳: `image_20250609_143022.png`
- 不添加时间戳: `image.png` (多图时自动添加索引 `image_001.png`)

##### 2. 文件保存器 - 自定义文件名

**节点名称**: "文件保存器 - 自定义文件名"

使用指定的固定文件名，忽略前缀和时间戳设置。

**必需参数:**
- **images**: 输入图像 (连接到图像生成节点)
- **save_path**: 保存路径 (默认: output/images)
- **custom_filename**: 自定义文件名 (默认: output)
- **file_format**: 文件格式 (png/jpg/jpeg/webp)
- **quality**: 图像质量 (1-100，默认95)

**可选参数:**
- **allow_overwrite**: 允许覆盖 (true: 覆盖同名文件 / false: 自动重命名，默认false)
- **create_subfolder**: 是否按日期创建子文件夹 (默认: false)
- **enable_osc**: 启用OSC消息发送 (默认: false)
- **osc_ip**: OSC接收端IP地址 (默认: 127.0.0.1)
- **osc_port**: OSC接收端端口 (默认: 8189)
- **osc_address**: OSC消息地址 (默认: /comfy/done)
- **osc_message**: 自定义OSC消息内容 (默认: 空，发送文件路径)

**使用场景:**
- 需要固定文件名的场景 (如 `latest.png`)
- 自动处理用户提供的扩展名

##### 3. 文件保存器 (旧版)

**节点名称**: "文件保存器 (旧版)"

兼容性节点，包含所有参数。建议使用上述两个新节点代替。

#### 覆盖控制

**允许覆盖 (allow_overwrite=true):**
- 如果文件已存在，直接覆盖
- 适用于需要固定文件名的场景 (如 `latest.png`)

**防止覆盖 (allow_overwrite=false):**
- 如果文件已存在，自动添加数字后缀
- 示例: `image.png` → `image_001.png`
- 确保不会丢失已有文件

#### OSC消息发送

**OSC (Open Sound Control)** 是一种网络通信协议，常用于音频/视频软件之间的实时通信。

**启用OSC (enable_osc=true):**
- 文件保存完成后自动发送OSC消息
- 可通知其他应用程序处理完成

**OSC配置参数:**
- **osc_ip**: 接收端IP地址 (127.0.0.1=本机, 192.168.1.100=局域网)
- **osc_port**: 接收端端口号 (1-65535)
- **osc_address**: 消息地址路径 (如 /comfy/done)
- **osc_message**: 自定义消息内容 (留空则发送文件路径)

**常见应用场景:**
- **TouchDesigner**: 触发视觉效果 ([集成教程](TDLink/README.md))
- **Max/MSP**: 音频处理触发
- **Ableton Live**: 音乐制作集成
- **自定义应用**: 工作流自动化

### 3. 连接输出

**即梦图像生成节点**输出：
- **image**: IMAGE 类型，可以连接到：
  - 文件保存器节点 (推荐)
  - SaveImage 节点
  - PreviewImage 节点
  - 其他图像处理节点

**文件保存器节点**输出：
- **images**: IMAGE 类型 (用于预览)
- **saved_path**: 保存的完整路径
- **filename**: 保存的文件名

## 注意事项

1. **API 配额**: 请注意火山引擎的 API 调用配额和计费 (按生成图片张数和token计费)
2. **网络连接**: 确保 ComfyUI 可以访问互联网
3. **密钥安全**: 不要在工作流文件中硬编码 API 密钥
4. **错误处理**: 如果 API 调用失败，节点会返回红色错误图像，检查控制台日志
5. **4.0限制**: 多图输入最多10张，总输出+输入<=15张；图片格式jpeg/png，大小<=10MB
6. **链接有效期**: url格式返回的下载链接24小时内有效，请及时保存
7. **依赖包**: python-osc 是必需依赖，已包含在 requirements.txt 中

## 版本历史

- **v1.1.0** (2025-09-29)：重构版本，节点分离到独立文件，支持三种文件保存节点、完善的模块化设计
- **v0.0.2** (2025-09-29)：集成Seedream 4.0，支持多图融合、组图输出、4K分辨率、流式输出等新功能
- **v0.0.1**：初始版本，支持Seedream 3.0基本文生图

## 故障排除

### 常见问题

1. **参数验证错误**
   ```
   Value not in list: file_format: '95' not in ['png', 'jpg', 'jpeg', 'webp']
   Value not in list: naming_mode: 'image' not in ['prefix_mode', 'custom_name']
   ```
   **解决方案**:
   - 重启ComfyUI以加载最新的节点定义
   - 检查工作流中的参数值是否正确
   - 确保使用的是v1.1.0或更高版本

2. **API 密钥错误**
   - 检查 API Key 是否正确
   - 确认已开通火山方舟大模型服务

3. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置

4. **图像生成失败**
   - 检查提示词是否符合内容政策
   - 尝试调整生成参数 (如size、stream)
   - 对于4.0组图，检查max_images设置

5. **文件保存失败**
   - 检查保存路径的权限
   - 使用绝对路径
   - 避免文件名中的特殊字符

6. **OSC功能问题**
   ```
   ⚠️ pythonosc未安装，OSC功能将不可用
   ```
   **解决方案**:
   - OSC依赖已在 requirements.txt 中，如果仍未安装，运行: `pip install python-osc`
   - 重启ComfyUI
   - 检查OSC接收端是否在监听指定端口
   - 验证IP地址和端口配置是否正确

### 调试信息

插件会在 ComfyUI 控制台输出详细的错误信息和API响应（如usage token消耗），请查看控制台日志进行故障排除。

## 许可证

GPL License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [火山引擎官网](https://www.volcengine.com/)
- [火山方舟大模型服务](https://www.volcengine.com/product/ark)
- [Seedream 4.0 API 文档](https://www.volcengine.com/docs/82379/1541523)
- [ComfyUI 官网](https://github.com/comfyanonymous/ComfyUI)
- [GitHub 仓库](https://github.com/weisiren000/comfyui-jimeng-api) (v1.1.0 已发布)

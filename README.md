# ComfyUI 即梦 API 插件

这是一个 ComfyUI 自定义节点插件，用于集成火山引擎即梦图像生成 API 和智能文件保存功能。

## 🏗️ 项目结构

```
comfyui-jimeng-api/
├── __init__.py                 # 主入口文件
├── nodes/                      # 节点模块
│   ├── __init__.py            # 节点注册
│   ├── jimeng_generator.py    # 即梦图像生成节点
│   └── file_saver.py          # 文件保存节点
├── utils/                      # 工具模块
│   ├── __init__.py            # 工具导出
│   ├── image_utils.py         # 图像处理工具
│   └── file_utils.py          # 文件操作工具
├── tests/                      # 测试文件
│   ├── __init__.py            # 测试模块
│   ├── test_file_saver.py     # 文件保存测试
│   ├── test_node_definition.py # 节点定义测试
│   └── workflows/             # 测试工作流
├── TDLink/                     # TouchDesigner集成
│   ├── README.md              # TouchDesigner集成教程
│   └── How2Link.png           # 连接示意图
├── config.example.json        # 配置示例
├── requirements.txt           # 依赖列表
└── README.md                  # 项目文档
```

## 功能特性

### 即梦图像生成节点
- ✅ 支持文本到图像生成
- ✅ 支持多种图像尺寸 (1024x1024, 864x1152, 1152x864, 1280x720, 720x1280, 832x1248, 1248x832, 1512x648)
- ✅ **无水印图像输出** - 使用 base64 格式获取无水印图像
- ✅ 简化的参数配置 - 只需要提示词和 API Key
- ✅ 错误处理和异常恢复
- ✅ 基于实际 API 测试的可靠实现

### 文件保存节点 (增强版)
- ✅ **双命名模式**: 前缀模式 + 自定义文件名模式
- ✅ **覆盖控制**: 允许覆盖 / 防止覆盖选项
- ✅ **OSC消息发送**: 文件保存完成后发送OSC通知
- ✅ **智能文件保存**到指定目录
- ✅ **自动创建目录结构**
- ✅ **多种图像格式** (PNG, JPG, JPEG, WebP)
- ✅ **灵活命名策略**: 时间戳、自定义名称、批量索引
- ✅ **按日期创建子文件夹**选项
- ✅ **智能文件名处理**: 自动去除扩展名、冲突处理
- ✅ **质量参数控制**和格式优化

## 安装方法

1. 将此插件文件夹复制到 ComfyUI 的 `custom_nodes` 目录下
2. 安装依赖包：`pip install -r requirements.txt`
3. **OSC功能 (可选)**: `pip install python-osc`
4. 重启 ComfyUI
5. 在节点菜单中找到 "即梦 API" 分类

## 使用方法

### 1. 获取 API 密钥

1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 开通火山方舟大模型服务
3. 获取 API Key

### 2. 配置节点

#### 即梦图像生成节点
在 ComfyUI 中添加 "即梦图像生成" 节点，配置以下参数：

**必需参数:**
- **prompt**: 图像生成提示词
- **api_key**: 火山引擎 API Key
- **model**: 模型选择 (默认: doubao-seedream-3-0-t2i-250415)
- **size**: 图像尺寸 (支持多种比例)
- **watermark**: 是否添加水印

**可选参数:**
- **seed**: 随机种子 (-1为随机)
- **guidance_scale**: 引导强度 (1.0-10.0)
- **response_format**: 响应格式 (b64_json/url)

#### 文件保存节点 (增强版)
在 ComfyUI 中添加 "文件保存器" 节点，配置以下参数：

**必需参数:**
- **images**: 输入图像 (连接到图像生成节点)
- **save_path**: 保存路径 (默认: output/images)
- **naming_mode**: 命名模式 (prefix_mode/custom_name)
- **filename_prefix**: 文件名前缀 (前缀模式下使用)
- **file_format**: 文件格式 (png/jpg/jpeg/webp)
- **quality**: 图像质量 (1-100)

**可选参数:**
- **custom_filename**: 自定义文件名 (自定义模式下使用)
- **allow_overwrite**: 允许覆盖 (true: 覆盖同名文件 / false: 自动重命名)
- **add_timestamp**: 是否添加时间戳 (仅前缀模式)
- **create_subfolder**: 是否按日期创建子文件夹
- **enable_osc**: 启用OSC消息发送 (默认: false)
- **osc_ip**: OSC接收端IP地址 (默认: 127.0.0.1)
- **osc_port**: OSC接收端端口 (默认: 8189)
- **osc_address**: OSC消息地址 (默认: /comfy/done)
- **osc_message**: 自定义OSC消息内容 (默认: 空，发送文件路径)

#### 命名模式说明

**前缀模式 (prefix_mode)**:
- 使用传统的 `前缀 + 时间戳 + 索引` 命名方式
- 示例: `image_20250609_143022.png`
- 适用于批量生成和版本管理

**自定义文件名模式 (custom_name)**:
- 使用指定的文件名，忽略前缀和时间戳设置
- 示例: `my_artwork.png`
- 适用于需要特定文件名的场景
- 自动处理用户提供的扩展名

#### 覆盖控制

**允许覆盖 (allow_overwrite=true)**:
- 如果文件已存在，直接覆盖
- 适用于需要固定文件名的场景 (如 `latest.png`)

**防止覆盖 (allow_overwrite=false)**:
- 如果文件已存在，自动添加数字后缀
- 示例: `image.png` → `image_001.png`
- 确保不会丢失已有文件

#### OSC消息发送

**OSC (Open Sound Control)** 是一种网络通信协议，常用于音频/视频软件之间的实时通信。

**启用OSC (enable_osc=true)**:
- 文件保存完成后自动发送OSC消息
- 可通知其他应用程序处理完成

**OSC配置参数**:
- **osc_ip**: 接收端IP地址 (127.0.0.1=本机, 192.168.1.100=局域网)
- **osc_port**: 接收端端口号 (1-65535)
- **osc_address**: 消息地址路径 (如 /comfy/done)
- **osc_message**: 自定义消息内容 (留空则发送文件路径)

**常见应用场景**:
- **TouchDesigner**: 触发视觉效果 ([集成教程](TDLink/README.md))
- **Max/MSP**: 音频处理触发
- **Ableton Live**: 音乐制作集成
- **自定义应用**: 工作流自动化

### 3. 连接输出

**即梦图像生成节点**输出 IMAGE 类型，可以连接到：
- 文件保存器节点 (推荐)
- SaveImage 节点
- PreviewImage 节点
- 其他图像处理节点

**文件保存器节点**输出：
- **saved_path**: 保存的完整路径
- **filename**: 保存的文件名

## 示例工作流

### 基础工作流
```
即梦图像生成 → 文件保存器
```

### 完整工作流示例

#### 基础工作流
```
即梦图像生成 → 文件保存器 → PreviewImage
              ↓
           saved_path (可连接到其他节点)
```

#### 高级工作流示例

**1. 批量生成 + 前缀模式**
```json
{
  "naming_mode": "prefix_mode",
  "filename_prefix": "artwork",
  "add_timestamp": true,
  "allow_overwrite": false
}
// 结果: artwork_20250609_143022.png
```

**2. 固定文件名 + 覆盖模式**
```json
{
  "naming_mode": "custom_name",
  "custom_filename": "latest_creation",
  "allow_overwrite": true
}
// 结果: latest_creation.png (每次覆盖)
```

**3. 版本管理模式**
```json
{
  "naming_mode": "custom_name",
  "custom_filename": "my_masterpiece",
  "allow_overwrite": false
}
// 结果: my_masterpiece.png, my_masterpiece_001.png, ...
```

**4. OSC集成模式**
```json
{
  "naming_mode": "custom_name",
  "custom_filename": "latest_render",
  "allow_overwrite": true,
  "enable_osc": true,
  "osc_ip": "127.0.0.1",
  "osc_port": 8189,
  "osc_address": "/comfy/done",
  "osc_message": "Render completed"
}
// 结果: latest_render.png + OSC消息发送
```

## 注意事项

1. **API 配额**: 请注意火山引擎的 API 调用配额和计费
2. **网络连接**: 确保 ComfyUI 可以访问互联网
3. **密钥安全**: 不要在工作流文件中硬编码 API 密钥
4. **错误处理**: 如果 API 调用失败，节点会返回红色错误图像

## 支持的模型

- doubao-seedream-3-0-t2i-250415 (默认)

## 故障排除

### 常见问题

1. **参数验证错误** (v1.2.1修复)
   ```
   Value not in list: file_format: '95' not in ['png', 'jpg', 'jpeg', 'webp']
   Value not in list: naming_mode: 'image' not in ['prefix_mode', 'custom_name']
   ```
   **解决方案**:
   - 重启ComfyUI以加载最新的节点定义
   - 检查工作流中的参数值是否正确
   - 确保使用的是v1.2.1或更高版本

2. **API 密钥错误**
   - 检查 API Key 是否正确
   - 确认已开通相应的模型服务

3. **网络连接问题**
   - 检查网络连接
   - 确认防火墙设置

4. **图像生成失败**
   - 检查提示词是否符合内容政策
   - 尝试调整生成参数

5. **文件保存失败**
   - 检查保存路径的权限
   - 使用绝对路径
   - 避免文件名中的特殊字符

6. **OSC功能问题**
   ```
   ⚠️ pythonosc未安装，OSC功能将不可用
   ```
   **解决方案**:
   - 安装OSC依赖: `pip install python-osc`
   - 重启ComfyUI
   - 检查OSC接收端是否在监听指定端口
   - 验证IP地址和端口配置是否正确

### 调试信息

插件会在 ComfyUI 控制台输出详细的错误信息，请查看控制台日志进行故障排除。

## 更新日志

### v1.3.0 - OSC集成版本
- ✅ **OSC消息发送**: 文件保存完成后发送OSC通知
- ✅ **OSC参数配置**: IP、端口、地址、消息内容完全可配置
- ✅ **应用集成支持**: TouchDesigner、Max/MSP、Ableton Live等
- ✅ **错误处理完善**: OSC发送失败不影响文件保存
- ✅ **示例代码提供**: OSC监听器示例和工作流模板
- ✅ **可选依赖**: OSC功能可选，不影响基础功能

### v1.2.1 - 参数验证修复版本
- ✅ **修复参数验证错误**: 解决"Value not in list"错误
- ✅ **向后兼容性优化**: 将新参数移至可选参数，保持原有参数顺序
- ✅ **参数顺序调整**: naming_mode等新参数不影响旧工作流
- ✅ **完善测试验证**: 新增参数验证和兼容性测试

### v1.2.0 - 文件保存器增强版本
- ✅ **双命名模式**: 新增自定义文件名模式，支持指定文件名
- ✅ **覆盖控制**: 新增覆盖开关，可选择覆盖或自动重命名
- ✅ **智能文件名处理**: 自动去除用户提供的文件扩展名
- ✅ **增强日志输出**: 显示命名模式和覆盖状态信息
- ✅ **向后兼容**: 保持原有前缀模式功能不变
- ✅ **完善测试**: 新增语法检查和功能验证测试
- ✅ **详细文档**: 更新使用说明和示例工作流

### v1.1.0 - 模块化重构版本
- ✅ **代码重构**: 将单一文件拆分为模块化结构
- ✅ **节点分离**: 即梦生成和文件保存节点独立文件
- ✅ **工具模块**: 图像处理和文件操作工具函数
- ✅ **测试完善**: 完整的测试文件和工作流示例
- ✅ **文档优化**: 详细的项目结构和使用说明
- ✅ **新增文件保存器节点**
- ✅ **支持自动目录创建**
- ✅ **支持多种图像格式保存**
- ✅ **支持时间戳和日期子文件夹**
- ✅ **智能文件名冲突处理**

### v1.0.0
- 初始版本
- 支持基本的文本到图像生成
- 支持参数配置和错误处理

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [火山引擎官网](https://www.volcengine.com/)
- [火山方舟大模型服务](https://www.volcengine.com/product/ark)
- [ComfyUI 官网](https://github.com/comfyanonymous/ComfyUI)
# comfyui-jimeng-api

# DOCX MCP 服务

一个基于 MCP (Model Context Protocol) 的 Word 文档处理服务，提供文档结构提取、内容修改和文件管理功能。

## ✨ 功能特性

- 📄 **文档结构提取**: 从 .docx 文件中提取段落、表格等结构化内容
- ✏️ **内容修改**: 支持批量修改文档中的文本内容
- ☁️ **云存储集成**: 自动上传修改后的文档到阿里云 OSS
- 🔗 **URL 支持**: 支持从 URL 直接下载和处理文档
- 🛠️ **MCP 兼容**: 完全兼容 MCP 协议，可集成到支持 MCP 的 AI 助手中

## 📋 系统要求

- Python 3.13+
- uvx (推荐) 或 uv (Python 包管理器)

### 为什么选择 uvx？

- 🚀 **即开即用**: 无需本地安装，直接运行
- 🔒 **环境隔离**: 自动管理依赖环境，避免冲突
- 📦 **轻量部署**: 类似 npx，适合工具型应用
- 🔄 **自动更新**: 每次运行使用最新版本

## 🚀 快速开始

### 安装方式

#### 方式一：从本地运行 uvx（当前推荐）

```bash
# 在项目目录下运行
uvx --from . docx-mcp

# 或使用 uv tool run
uv tool run --from . docx-mcp
```

#### 方式二：发布后使用 uvx（未来推荐）

```bash
# 发布到 PyPI 后可以直接运行
uvx docx-mcp
```

#### 方式三：本地开发安装

```bash
# 使用 uv 安装依赖
uv sync

# 或使用 pip 从 pyproject.toml 安装
pip install -e .
```

### 配置 MCP 服务

#### 使用 uvx 从本地运行（当前推荐配置）

在 Cursor 的 `mcp.json` 配置文件中添加以下配置：

```json
{
  "mcpServers": {
    "docx_filler_service": {
      "command": "cmd",
      "args": [
        "/c",
        "uvx",
        "--from",
        "C:\\Users\\你的用户名\\Desktop\\docx_mcp",
        "docx-mcp"
      ]
    }
  }
}
```

#### 使用 uvx 从 PyPI（发布后）

```json
{
  "mcpServers": {
    "docx_filler_service": {
      "command": "cmd",
      "args": [
        "/c",
        "uvx",
        "docx-mcp"
      ]
    }
  }
}
```

#### 使用本地 uv（开发模式）

```json
{
  "mcpServers": {
    "docx_filler_service": {
      "command": "cmd",
      "args": [
        "/c",
        "uv",
        "--directory",
        "C:\\Users\\你的用户名\\Desktop\\docx_mcp",
        "run",
        "main.py"
      ]
    }
  }
}
```

### 启动服务

```bash
# 使用 uvx 从本地运行（当前推荐）
uvx --from . docx-mcp

# 使用 uvx 从 PyPI（发布后）
uvx docx-mcp

# 使用 uv 运行（开发模式）
uv run main.py

# 或直接运行
python main.py
```

## 📦 发布到 PyPI

如果您想要发布包以便全局使用 uvx：

### 快速配置（推荐）

```bash
# 1. 运行凭证配置脚本
python setup_pypi_credentials.py

# 2. 运行发布脚本
python publish.py
```

### 手动配置

```bash
# 1. 设置 PyPI 凭证
$env:TWINE_USERNAME = "your-pypi-username"
$env:TWINE_PASSWORD = "your-pypi-password"

# 2. 构建包
uv build

# 3. 发布到 PyPI
pip install twine
twine upload dist/*
```

发布后，任何人都可以直接使用：
```bash
uvx docx-mcp
```

## 🔧 API 功能

### 1. 提取文档结构

```python
extract_document_structure(document_url: str) -> Dict
```

从 URL 下载 .docx 文件并提取其结构，为每个元素分配唯一 ID。

**参数:**
- `document_url`: .docx 文件的 URL 链接

**返回:** 包含文档结构的字典，每个元素都有唯一的 ID

### 2. 应用文档修改

```python
apply_modifications_to_document(
    original_file_content_base64: str, 
    patches_json: str
) -> str
```

将一系列修改应用到 .docx 文件，返回修改后的文件内容。

**参数:**
- `original_file_content_base64`: 原始 .docx 文件的 Base64 编码
- `patches_json`: JSON 格式的修改指令列表

**示例修改指令:**
```json
[
  {
    "element_id": "p_0",
    "new_content": "新的段落内容"
  },
  {
    "element_id": "table_0_cell_0_0",
    "new_content": "新的表格单元格内容"
  }
]
```

### 3. 获取修改后的文档

```python
get_modified_document(
    original_file_content_base64: str, 
    patches_json: str
) -> str
```

`apply_modifications_to_document` 的别名，用于更清晰地表达获取最终结果的意图。

### 4. 准备文档下载

```python
prepare_document_for_download(
    original_file_content_base64: str, 
    patches_json: str
) -> Dict
```

将修改后的文档上传到阿里云 OSS，返回下载链接。

**返回示例:**
```json
{
  "success": true,
  "download_url": "https://ggb-lzt.oss-cn-shenzhen.aliyuncs.com/modified_document_xxx.docx",
  "file_name": "modified_document_xxx.docx"
}
```

### 5. 从 URL 处理文档

```python
process_document_from_url(
    document_url: str, 
    patches_json: str
) -> Dict
```

直接从 URL 下载文档，应用修改，然后上传到 OSS。

## 📁 项目结构

```
docx_mcp/
├── core/                    # 核心功能模块
│   ├── docx_processor.py   # 文档处理器
│   └── models.py           # 数据模型定义
├── dist/                   # 构建输出目录
│   ├── docx_mcp-0.1.0-py3-none-any.whl
│   └── docx_mcp-0.1.0.tar.gz
├── main.py                 # MCP 服务主入口
├── pyproject.toml         # 项目配置和依赖定义
├── requirements.txt       # 备用依赖文件（兼容性）
├── uv.lock               # uv 锁定文件
├── LICENSE               # MIT 许可证
├── PUBLISH.md            # 发布指南
├── PRE_PUBLISH_CHECKLIST.md  # 发布前检查清单
├── READY_TO_PUBLISH.md   # 发布准备说明
├── setup_pypi_credentials.py # PyPI 凭证配置脚本
├── publish.py            # 自动化发布脚本
├── env.example           # 环境变量配置模板
└── README.md             # 项目文档
```

## 🔐 配置说明

### 阿里云 OSS 配置

推荐使用环境变量配置 OSS 访问信息。复制 `env.example` 文件并重命名为 `.env`，然后填入您的实际配置：

```bash
# 复制配置模板
cp env.example .env
```

在 `.env` 文件中设置：

```bash
OSS_ACCESS_KEY=your_access_key_here
OSS_SECRET_KEY=your_secret_key_here
OSS_BUCKET_NAME=your_bucket_name
OSS_DOMAIN=https://your-bucket.oss-cn-shenzhen.aliyuncs.com/
```

或者在系统环境变量中设置：

```bash
# Windows PowerShell
$env:OSS_ACCESS_KEY = "your_access_key_here"
$env:OSS_SECRET_KEY = "your_secret_key_here"
$env:OSS_BUCKET_NAME = "your_bucket_name"
$env:OSS_DOMAIN = "https://your-bucket.oss-cn-shenzhen.aliyuncs.com/"

# PyPI 发布凭证（可选）
$env:TWINE_USERNAME = "your-pypi-username"
$env:TWINE_PASSWORD = "your-pypi-password"

# Linux/macOS
export OSS_ACCESS_KEY="your_access_key_here"
export OSS_SECRET_KEY="your_secret_key_here"
export OSS_BUCKET_NAME="your_bucket_name"
export OSS_DOMAIN="https://your-bucket.oss-cn-shenzhen.aliyuncs.com/"

# PyPI 发布凭证（可选）
export TWINE_USERNAME="your-pypi-username"
export TWINE_PASSWORD="your-pypi-password"
```

⚠️ **安全提示**: 
- 请不要将敏感信息提交到版本控制系统
- `.env` 文件已添加到 `.gitignore` 中
- 生产环境建议使用更安全的密钥管理方案

## 🛠️ 开发指南

### 数据模型

项目使用 Pydantic 定义数据模型：

```python
class DocumentPatch(BaseModel):
    element_id: str      # 元素唯一标识符
    new_content: Any     # 新内容（支持多种类型）
```

### 扩展功能

要添加新的文档处理功能：

1. 在 `core/docx_processor.py` 中实现处理逻辑
2. 在 `main.py` 中使用 `@mcp.tool()` 装饰器注册新的 MCP 工具
3. 更新相关的数据模型

## 🤝 贡献指南

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🔗 相关链接

- [MCP 官方文档](https://modelcontextprotocol.io/)
- [FastMCP 框架](https://github.com/pydantic/fastmcp)
- [python-docx 文档](https://python-docx.readthedocs.io/)
- [阿里云 OSS Python SDK](https://help.aliyun.com/document_detail/32026.html)

## ❓ 常见问题

### Q: uvx 和 uv 有什么区别？
A: uvx 是用于运行独立 Python 工具的工具，类似 npx。它会自动处理依赖和环境隔离，更适合工具型应用。uv 主要用于项目依赖管理和开发。

### Q: 如何处理大文件？
A: 服务支持通过 Base64 编码处理大文件，但建议文件大小不超过 50MB。

### Q: 支持哪些文档格式？
A: 目前仅支持 .docx 格式（Office 2007+ 格式）。

### Q: 如何自定义 OSS 配置？
A: 修改 `main.py` 中的 `OSS_CONFIG` 字典，或考虑使用环境变量。

### Q: uvx 找不到命令怎么办？
A: 确保已安装 uv，然后 uvx 会自动可用。如果仍有问题，可以使用 `uv tool run docx-mcp` 替代。

---

💡 **提示**: 如有问题或建议，欢迎提交 Issue 或 Pull Request！

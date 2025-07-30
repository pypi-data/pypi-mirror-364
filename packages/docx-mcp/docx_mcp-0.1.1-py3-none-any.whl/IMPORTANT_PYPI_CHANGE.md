# ⚠️ 重要：PyPI 认证方式变更

## 🚨 紧急通知

**PyPI 已经完全停止支持用户名/密码认证！**

从错误信息可以看到：
```
403 Username/Password authentication is no longer supported. 
Migrate to API Tokens or Trusted Publishers instead.
```

## 🔧 解决方案

### 必须使用 API Token

您**必须**使用 API Token 来发布到 PyPI，用户名/密码方式已经完全废弃。

### 获取 API Token 的步骤

1. **登录 PyPI**
   - 访问 [https://pypi.org/](https://pypi.org/)
   - 使用您的用户名和密码登录

2. **生成 API Token**
   - 访问 [https://pypi.org/manage/account/](https://pypi.org/manage/account/)
   - 滚动到 "API tokens" 部分
   - 点击 "Add API token"
   - 设置 Token 名称（如：docx-mcp-upload）
   - 选择 Scope：
     - "Entire account" 或
     - "Project: docx-mcp"（如果项目已存在）

3. **复制 Token**
   - 复制生成的 token（格式：`pypi-AgEIcHlwaS5vcmcC...`）
   - ⚠️ **重要**：Token 只显示一次，请立即保存！

### 设置认证

使用以下格式设置环境变量：

```bash
# Windows PowerShell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-您的完整token字符串"

# Linux/macOS
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="pypi-您的完整token字符串"
```

**注意**：
- 用户名必须是 `__token__`（两个下划线）
- 密码是完整的 token 字符串（以 `pypi-` 开头）

## 🔄 更新配置文件

更新 `~/.pypirc` 文件：

```ini
[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = pypi-您的token

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-您的testpypi-token
```

## 📝 更新后的发布流程

1. 获取 API Token
2. 设置环境变量
3. 运行发布命令：
   ```bash
   twine upload dist/*
   ```

## 🔗 相关链接

- [PyPI API Tokens 帮助](https://pypi.org/help/#apitoken)
- [PyPI Account Settings](https://pypi.org/manage/account/)
- [Trusted Publishers](https://pypi.org/help/#trusted-publishers) 
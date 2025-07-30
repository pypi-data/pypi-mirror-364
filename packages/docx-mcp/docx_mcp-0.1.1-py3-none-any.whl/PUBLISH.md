# 发布到 PyPI 指南

## 准备工作

### 1. 获取 PyPI API Token

⚠️ **重要**：PyPI 已停止支持用户名/密码认证，必须使用 API Token！

1. 访问 [PyPI](https://pypi.org/) 并登录账户
2. 访问 [Account Settings](https://pypi.org/manage/account/)
3. 在 "API tokens" 部分创建新的 token
4. 复制生成的 token（格式：`pypi-xxx...`）

### 2. 配置环境变量

在您的系统中设置以下环境变量：

```bash
# Windows PowerShell
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-your-token-here"

# Windows CMD
set TWINE_USERNAME=__token__
set TWINE_PASSWORD=pypi-your-token-here

# Linux/macOS
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here
```

## 发布步骤

### 方法1：使用 uv publish（推荐）

```bash
# 确保已构建
uv build

# 发布到 PyPI
uv publish
```

### 方法2：使用 twine

```bash
# 安装 twine
pip install twine

# 检查包
twine check dist/*

# 上传到 TestPyPI（测试）
twine upload --repository testpypi dist/*

# 上传到 PyPI（正式发布）
twine upload dist/*
```

## 测试发布

### 使用 TestPyPI 测试

1. 先发布到 TestPyPI：
```bash
twine upload --repository testpypi dist/*
```

2. 测试安装：
```bash
uvx --index-url https://test.pypi.org/simple/ docx-mcp
```

### 验证正式发布

发布到 PyPI 后，测试：
```bash
uvx docx-mcp
```

## 发布前检查清单

- [ ] 更新版本号（在 `pyproject.toml` 中）
- [ ] 更新 README.md
- [ ] 检查敏感信息已移除
- [ ] 运行测试
- [ ] 构建包无错误
- [ ] 在 TestPyPI 测试通过

## 版本管理

每次发布新版本时：

1. 更新 `pyproject.toml` 中的版本号
2. 提交代码到 Git
3. 创建 Git tag：
```bash
git tag v0.1.0
git push origin v0.1.0
```
4. 重新构建和发布

## 注意事项

⚠️ **重要**：
- 确保敏感信息（如 API 密钥）已移除或使用环境变量
- 版本号不能重复，每次发布必须递增
- 发布到 PyPI 后无法删除，只能发布新版本
- 建议先在 TestPyPI 测试 
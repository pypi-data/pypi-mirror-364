# 发布前检查清单

在运行 `python publish.py` 或手动发布到 PyPI 之前，请确保完成以下所有检查项：

## ✅ 代码质量检查

- [ ] 代码已提交到 Git 仓库
- [ ] 所有测试通过
- [ ] 代码无明显错误或警告
- [ ] 移除了所有调试代码和注释

## ✅ 安全检查

- [ ] **重要**: 移除了所有敏感信息（API密钥、密码等）
- [ ] 敏感配置已改为环境变量
- [ ] `.env` 文件已添加到 `.gitignore`
- [ ] 检查了所有文件，确保无敏感信息泄露

## ✅ 元数据检查

- [ ] `pyproject.toml` 中的版本号已更新
- [ ] 作者信息和邮箱已正确填写
- [ ] 项目描述清晰准确
- [ ] GitHub 仓库链接正确
- [ ] 许可证信息正确

## ✅ 文档检查

- [ ] `README.md` 内容完整且准确
- [ ] 安装说明清晰
- [ ] 使用示例可运行
- [ ] API 文档完整
- [ ] 更新日志记录了此版本的变更

## ✅ 功能测试

- [ ] 包能正确构建 (`uv build`)
- [ ] 包通过 twine 检查 (`twine check dist/*`)
- [ ] 本地安装测试通过 (`uvx --from . docx-mcp`)
- [ ] 核心功能正常工作
- [ ] MCP 协议兼容性测试通过

## ✅ PyPI 准备

- [ ] 拥有 PyPI 账户
- [ ] 账户邮箱已验证
- [ ] 设置了 `TWINE_USERNAME` 和 `TWINE_PASSWORD` 环境变量（用户名和密码）
- [ ] 包名 `docx-mcp` 在 PyPI 上可用（未被占用）

## ✅ 发布流程

- [ ] 先在 TestPyPI 测试发布
- [ ] 从 TestPyPI 安装测试通过
- [ ] 创建 Git tag 标记版本
- [ ] 准备好发布说明

## 🚀 发布命令

### 自动发布（推荐）
```bash
python publish.py
```

### 手动发布
```bash
# 构建
uv build

# 检查
twine check dist/*

# 测试上传
twine upload --repository testpypi dist/*

# 正式上传
twine upload dist/*
```

## ⚠️ 重要提醒

1. **版本号不能重复** - 每次发布必须递增版本号
2. **无法撤销** - 发布到 PyPI 后无法删除，只能发布新版本
3. **安全第一** - 确保没有敏感信息泄露
4. **测试充分** - 在 TestPyPI 充分测试后再发布到正式 PyPI

## 📝 发布后

- [ ] 验证包可以通过 `uvx docx-mcp` 安装
- [ ] 更新项目文档中的安装说明
- [ ] 创建 GitHub Release
- [ ] 通知用户新版本发布 
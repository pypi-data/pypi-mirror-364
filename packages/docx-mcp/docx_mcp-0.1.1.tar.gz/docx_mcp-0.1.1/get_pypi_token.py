#!/usr/bin/env python3
"""
PyPI API Token 设置脚本
帮助用户快速设置PyPI API Token进行发布
"""

import os
import webbrowser
import getpass

def open_pypi_account():
    """打开PyPI账户设置页面"""
    print("🌐 正在打开 PyPI 账户设置页面...")
    webbrowser.open("https://pypi.org/manage/account/")
    print("✅ 已在浏览器中打开 PyPI 账户设置页面")

def get_token_instructions():
    """显示获取token的详细说明"""
    print("\n📋 获取 API Token 的步骤：")
    print("=" * 50)
    print("1. 登录到 PyPI 账户")
    print("2. 滚动到 'API tokens' 部分")
    print("3. 点击 'Add API token'")
    print("4. 设置 Token 名称（建议：docx-mcp-upload）")
    print("5. 选择 Scope：")
    print("   - 'Entire account'（推荐用于新项目）")
    print("   - 或 'Project: docx-mcp'（如果项目已存在）")
    print("6. 点击 'Add token'")
    print("7. **重要**：立即复制生成的 token！（只显示一次）")
    print("\n⚠️  Token 格式类似：pypi-AgEIcHlwaS5vcmcCJG...")

def set_token():
    """设置API Token"""
    print("\n🔐 设置 API Token")
    print("=" * 30)
    
    # 获取token
    token = getpass.getpass("请粘贴您的 PyPI API Token: ").strip()
    
    if not token:
        print("❌ Token 不能为空")
        return False
    
    if not token.startswith('pypi-'):
        print("❌ Token 格式不正确，应该以 'pypi-' 开头")
        return False
    
    # 确认设置
    print(f"\n📋 确认信息:")
    print(f"Token: {token[:20]}...{token[-10:]}")  # 只显示部分token
    
    confirm = input("\n确认设置这个 Token？ (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 取消设置")
        return False
    
    # 设置环境变量
    try:
        os.environ['TWINE_USERNAME'] = '__token__'
        os.environ['TWINE_PASSWORD'] = token
        
        print("\n✅ Token 已设置到当前会话")
        
        if os.name == 'nt':
            print("\n💡 要永久设置，请手动运行以下命令:")
            print(f'$env:TWINE_USERNAME = "__token__"')
            print(f'$env:TWINE_PASSWORD = "{token}"')
        else:
            print("\n💡 要永久设置，请在 ~/.bashrc 或 ~/.zshrc 中添加:")
            print(f'export TWINE_USERNAME="__token__"')
            print(f'export TWINE_PASSWORD="{token}"')
        
        # 询问是否创建.pypirc
        setup_pypirc = input("\n是否要创建 .pypirc 配置文件？ (y/N): ").strip().lower()
        if setup_pypirc == 'y':
            create_pypirc(token)
        
        return True
        
    except Exception as e:
        print(f"❌ 设置 Token 时出错: {e}")
        return False

def create_pypirc(token):
    """创建.pypirc配置文件"""
    pypirc_path = os.path.expanduser("~/.pypirc")
    
    pypirc_content = f"""[distutils]
index-servers = pypi testpypi

[pypi]
username = __token__
password = {token}

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = {token}
"""
    
    try:
        with open(pypirc_path, 'w', encoding='utf-8') as f:
            f.write(pypirc_content)
        
        # 设置文件权限（仅所有者可读写）
        if os.name != 'nt':
            os.chmod(pypirc_path, 0o600)
        
        print(f"✅ 已创建 {pypirc_path}")
        print("⚠️  注意：Token 以明文存储，请确保文件安全")
        
    except Exception as e:
        print(f"❌ 创建 .pypirc 失败: {e}")

def test_setup():
    """测试设置"""
    print("\n🧪 测试设置...")
    
    username = os.getenv('TWINE_USERNAME')
    password = os.getenv('TWINE_PASSWORD')
    
    if username == '__token__' and password and password.startswith('pypi-'):
        print("✅ Token 配置正确")
        print(f"用户名: {username}")
        print(f"Token: {password[:20]}...{password[-10:]}")
        return True
    else:
        print("❌ Token 配置不正确")
        return False

def show_next_steps():
    """显示下一步操作"""
    print("\n🚀 下一步操作:")
    print("1. 运行发布脚本: python publish.py")
    print("2. 或手动发布: twine upload dist/*")
    print("3. 如果发布失败，请检查 Token 是否正确")

def main():
    """主函数"""
    print("🔐 PyPI API Token 设置工具")
    print("=" * 50)
    print("⚠️  重要：PyPI 已停止支持用户名/密码认证")
    print("📖 必须使用 API Token 进行发布")
    
    # 询问是否需要打开账户页面
    open_page = input("\n是否要打开 PyPI 账户设置页面？ (Y/n): ").strip().lower()
    if open_page != 'n':
        open_pypi_account()
    
    # 显示获取token的说明
    get_token_instructions()
    
    # 等待用户获取token
    input("\n按 Enter 继续设置 Token...")
    
    # 设置token
    if not set_token():
        print("❌ Token 设置失败")
        return
    
    # 测试设置
    if not test_setup():
        print("❌ 设置验证失败")
        return
    
    # 显示下一步
    show_next_steps()
    
    print("\n🎉 Token 设置完成！")

if __name__ == "__main__":
    main() 
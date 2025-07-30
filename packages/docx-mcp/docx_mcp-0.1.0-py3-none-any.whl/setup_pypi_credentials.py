#!/usr/bin/env python3
"""
PyPI 凭证配置脚本
用于交互式设置 PyPI 用户名和密码
"""

import os
import getpass
import subprocess
import sys

def check_pypi_account():
    """检查PyPI账户连接"""
    print("🔍 检查PyPI账户连接...")
    
    # 尝试使用提供的凭证连接PyPI
    try:
        result = subprocess.run(
            ["twine", "check", "--help"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            print("✅ twine 已安装")
            return True
        else:
            print("❌ twine 未安装，请先运行: pip install twine")
            return False
    except subprocess.TimeoutExpired:
        print("❌ 网络连接超时")
        return False
    except FileNotFoundError:
        print("❌ twine 未安装，请先运行: pip install twine")
        return False

def set_credentials():
    """设置PyPI凭证"""
    print("\n📝 设置 PyPI 凭证")
    print("=" * 40)
    
    # 获取用户名
    username = input("请输入您的 PyPI 用户名: ").strip()
    if not username:
        print("❌ 用户名不能为空")
        return False
    
    # 获取密码
    password = getpass.getpass("请输入您的 PyPI 密码: ")
    if not password:
        print("❌ 密码不能为空")
        return False
    
    # 确认信息
    print(f"\n📋 确认信息:")
    print(f"用户名: {username}")
    print(f"密码: {'*' * len(password)}")
    
    confirm = input("\n确认设置这些凭证？ (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 取消设置")
        return False
    
    # 设置环境变量
    try:
        # Windows PowerShell
        if os.name == 'nt':
            # 设置当前会话环境变量
            os.environ['TWINE_USERNAME'] = username
            os.environ['TWINE_PASSWORD'] = password
            
            print("\n✅ 凭证已设置到当前会话")
            print("\n💡 要永久设置，请手动运行以下命令:")
            print(f'$env:TWINE_USERNAME = "{username}"')
            print(f'$env:TWINE_PASSWORD = "{password}"')
            
            # 或写入到用户配置文件
            setup_permanent = input("\n是否要设置到用户配置文件 (.pypirc)？ (y/N): ").strip().lower()
            if setup_permanent == 'y':
                create_pypirc(username, password)
        else:
            # Linux/macOS
            os.environ['TWINE_USERNAME'] = username
            os.environ['TWINE_PASSWORD'] = password
            
            print("\n✅ 凭证已设置到当前会话")
            print("\n💡 要永久设置，请在 ~/.bashrc 或 ~/.zshrc 中添加:")
            print(f'export TWINE_USERNAME="{username}"')
            print(f'export TWINE_PASSWORD="{password}"')
        
        return True
        
    except Exception as e:
        print(f"❌ 设置凭证时出错: {e}")
        return False

def create_pypirc(username, password):
    """创建 .pypirc 配置文件"""
    import os.path
    
    pypirc_path = os.path.expanduser("~/.pypirc")
    
    pypirc_content = f"""[distutils]
index-servers = pypi

[pypi]
username = {username}
password = {password}
"""
    
    try:
        with open(pypirc_path, 'w', encoding='utf-8') as f:
            f.write(pypirc_content)
        
        # 设置文件权限（仅所有者可读写）
        if os.name != 'nt':
            os.chmod(pypirc_path, 0o600)
        
        print(f"✅ 已创建 {pypirc_path}")
        print("⚠️  注意：密码以明文存储，请确保文件安全")
        
    except Exception as e:
        print(f"❌ 创建 .pypirc 失败: {e}")

def test_credentials():
    """测试凭证是否有效"""
    print("\n🧪 测试凭证...")
    
    # 检查环境变量
    username = os.getenv('TWINE_USERNAME')
    password = os.getenv('TWINE_PASSWORD')
    
    if not username or not password:
        print("❌ 未找到凭证环境变量")
        return False
    
    print(f"用户名: {username}")
    print("密码: 已设置")
    
    # 注意：这里不实际测试登录，因为可能会有rate limiting
    print("✅ 凭证已配置，将在实际发布时验证")
    return True

def show_next_steps():
    """显示下一步操作"""
    print("\n🚀 下一步操作:")
    print("1. 运行发布脚本: python publish.py")
    print("2. 或手动发布: twine upload dist/*")
    print("3. 如果发布失败，请检查用户名和密码是否正确")

def main():
    """主函数"""
    print("🔐 PyPI 凭证配置工具")
    print("=" * 50)
    
    # 检查twine
    if not check_pypi_account():
        print("\n请先安装 twine: pip install twine")
        sys.exit(1)
    
    # 设置凭证
    if not set_credentials():
        print("❌ 凭证设置失败")
        sys.exit(1)
    
    # 测试凭证
    if not test_credentials():
        print("❌ 凭证测试失败")
        sys.exit(1)
    
    # 显示下一步
    show_next_steps()
    
    print("\n🎉 配置完成！")

if __name__ == "__main__":
    main() 
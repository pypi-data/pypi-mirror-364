# #!/usr/bin/env python3
# """
# PyPI发布脚本
# 请在运行此脚本前阅读 PUBLISH.md
# """

# import os
# import sys
# import subprocess
# from pathlib import Path

# def run_command(cmd, check=True):
#     """运行命令并输出结果"""
#     print(f"运行: {cmd}")
#     result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
#     if result.stdout:
#         print(f"输出: {result.stdout}")
#     if result.stderr:
#         print(f"错误: {result.stderr}")
#     if check and result.returncode != 0:
#         print(f"命令失败，退出码: {result.returncode}")
#         sys.exit(1)
#     return result

# def check_environment():
#     """检查发布环境"""
#     print("🔍 检查发布环境...")
    
#     # 检查是否在git仓库中
#     if not Path('.git').exists():
#         print("❌ 当前目录不是git仓库")
#         return False
    
#     # 检查是否有未提交的更改
#     result = run_command("git status --porcelain", check=False)
#     if result.stdout.strip():
#         print("⚠️  有未提交的更改:")
#         print(result.stdout)
#         response = input("是否继续？ (y/N): ")
#         if response.lower() != 'y':
#             return False
    
#     # 检查环境变量
#     twine_username = os.getenv('TWINE_USERNAME')
#     twine_password = os.getenv('TWINE_PASSWORD')
    
#     if not twine_username or not twine_password:
#         print("❌ 未设置 TWINE_USERNAME 和 TWINE_PASSWORD 环境变量")
#         print("请参考 PUBLISH.md 设置 PyPI 用户名和密码")
#         return False
    
#     print("✅ 环境检查通过")
#     return True

# def build_package():
#     """构建包"""
#     print("\n📦 构建包...")
    
#     # 清理之前的构建
#     if Path('dist').exists():
#         run_command("rm -rf dist" if os.name != 'nt' else "rmdir /s /q dist", check=False)
    
#     # 构建
#     run_command("uv build")
    
#     # 检查构建结果
#     run_command("twine check dist/*")
#     print("✅ 包构建成功")

# def test_upload():
#     """上传到 TestPyPI 测试"""
#     print("\n🧪 上传到 TestPyPI 进行测试...")
#     response = input("是否要先上传到 TestPyPI 测试？ (Y/n): ")
    
#     if response.lower() != 'n':
#         try:
#             run_command("twine upload --repository testpypi dist/*")
#             print("✅ 上传到 TestPyPI 成功")
#             print("请测试安装:")
#             print("uvx --index-url https://test.pypi.org/simple/ docx-mcp")
#             input("测试完成后按 Enter 继续...")
#         except:
#             print("❌ 上传到 TestPyPI 失败")
#             return False
    
#     return True

# def upload_to_pypi():
#     """上传到正式 PyPI"""
#     print("\n🚀 准备上传到 PyPI...")
    
#     # 最后确认
#     print("⚠️  即将上传到正式 PyPI！")
#     print("注意：")
#     print("- 版本号不能重复")
#     print("- 上传后无法删除")
#     print("- 确保包已经测试完毕")
    
#     response = input("确认上传到 PyPI？ (yes/no): ")
#     if response.lower() != 'yes':
#         print("❌ 取消上传")
#         return False
    
#     try:
#         run_command("twine upload dist/*")
#         print("🎉 上传到 PyPI 成功！")
#         print("\n现在可以使用以下命令安装:")
#         print("uvx docx-mcp")
#         return True
#     except:
#         print("❌ 上传到 PyPI 失败")
#         return False

# def main():
#     """主函数"""
#     print("🚀 DOCX-MCP PyPI 发布脚本")
#     print("=" * 50)
    
#     # 检查环境
#     if not check_environment():
#         print("❌ 环境检查失败")
#         sys.exit(1)
    
#     # 构建包
#     build_package()
    
#     # 测试上传
#     if not test_upload():
#         print("❌ 测试上传失败")
#         sys.exit(1)
    
#     # 正式上传
#     if upload_to_pypi():
#         print("\n🎉 发布完成！")
#     else:
#         print("\n❌ 发布失败")
#         sys.exit(1)

# if __name__ == "__main__":
#     main() 
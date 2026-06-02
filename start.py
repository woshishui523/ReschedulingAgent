# start.py
# !/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速启动脚本
直接运行此文件即可启动列车晚点智能调度系统
"""
import subprocess
import sys


def check_dependencies():
    """检查依赖是否已安装"""
    required_packages = ['sqlalchemy', 'pymysql', 'langchain', 'openai']
    missing = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print("⚠️  缺少以下依赖包:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n请运行以下命令安装依赖:")
        print("   pip install -r requirements.txt\n")
        return False

    return True


def main():
    """主函数"""
    print("=" * 70)
    print("🚄 列车晚点智能调度系统")
    print("=" * 70)

    if not check_dependencies():
        sys.exit(1)

    print("\n✅ 依赖检查通过")
    print("\n正在启动系统...\n")

    try:
        subprocess.run([sys.executable, "run.py"])
    except KeyboardInterrupt:
        print("\n\n👋 系统已退出")
    except Exception as e:
        print(f"\n❌ 启动失败：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

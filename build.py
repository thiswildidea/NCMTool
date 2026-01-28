#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本
使用PyInstaller将应用打包成可执行文件
"""

import os
import platform
import subprocess

def build():
    """执行打包操作"""
    system = platform.system()
    
    # 安装依赖
    print("安装依赖...")
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
    
    # 安装PyInstaller
    print("安装PyInstaller...")
    subprocess.run(['pip', 'install', 'pyinstaller'], check=True)
    
    # 构建命令
    build_cmd = [
        'pyinstaller',
        '--name', '网络配置管理工具',
        '--onefile',
        '--windowed',
        'network_config_tool.py'
    ]
    
    print(f"执行打包命令: {' '.join(build_cmd)}")
    subprocess.run(build_cmd, check=True)
    
    print("打包完成!")
    print(f"可执行文件位置: dist/{'网络配置管理工具.exe' if system == 'Windows' else '网络配置管理工具'}")

if __name__ == "__main__":
    build()
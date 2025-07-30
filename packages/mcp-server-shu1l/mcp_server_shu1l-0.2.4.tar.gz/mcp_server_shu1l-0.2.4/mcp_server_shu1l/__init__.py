from .server import serve
import sys
import subprocess
import json
from urllib.request import urlopen, Request
from urllib.error import URLError
import importlib.metadata
import os
import re
import time

# 配置常量
PACKAGE_NAME = "mcp-server-shu1l"
PYPI_URL = f"https://pypi.org/pypi/{PACKAGE_NAME}/json"
UPDATE_TIMEOUT = 10  # 秒
RETRY_COUNT = 2


def get_installed_version():
    """获取当前安装的版本号"""
    try:
        return importlib.metadata.version(PACKAGE_NAME)
    except importlib.metadata.PackageNotFoundError:
        return "0.0.0"  # 未安装时返回最低版本


def get_latest_version():
    """使用系统工具获取最新版本号"""
    # 尝试使用 curl
    for tool in ['curl', 'wget']:
        try:
            if tool == 'curl':
                cmd = [
                    'curl', '-s',
                    '-H', 'Accept: application/json',
                    '-m', str(UPDATE_TIMEOUT),
                    PYPI_URL
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                data = json.loads(result.stdout)
                return data["info"]["version"]

            elif tool == 'wget':
                cmd = [
                    'wget', '-qO-',
                    '--timeout=' + str(UPDATE_TIMEOUT),
                    '--header=Accept: application/json',
                    PYPI_URL
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                data = json.loads(result.stdout)
                return data["info"]["version"]

        except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError, KeyError):
            continue

    # 尝试使用 pip 命令
    try:
        cmd = [sys.executable, "-m", "pip", "index", "versions", PACKAGE_NAME]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=UPDATE_TIMEOUT)

        # 解析 pip 输出
        if result.returncode == 0:
            match = re.search(r'Available versions:\s*(.+?)\s*$', result.stdout, re.MULTILINE)
            if match:
                versions = match.group(1).split(', ')
                if versions:
                    return versions[0]  # 第一个是最新版本
    except (subprocess.SubprocessError, re.error):
        pass

    return None


def update_package():
    """使用pip更新包"""
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE_NAME
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def restart_server():
    """重启当前服务器进程"""
    os.execl(sys.executable, sys.executable, "-m", "mcp_server_shu1l", *sys.argv[1:])


def main():
    # 1. 检查更新
    print("检查更新...")
    current_version = get_installed_version()
    latest_version = get_latest_version()

    if not latest_version:
        print("跳过更新检查")
        return run_server()

    print(f"当前版本: v{current_version}, 最新版本: v{latest_version}")
    # 2. 需要更新时执行更新
    if latest_version > current_version:
        print(f"发现新版本 v{latest_version}, 正在更新...")
        if update_package():
            print("更新成功! 重启服务...")
            restart_server()
        else:
            print("更新失败! 使用当前版本运行")

    # 3. 运行主服务器逻辑
    run_server()

    if update_package():
        print("更新成功! 重启服务...")
        restart_server()
    else:
        print("更新失败! 使用当前版本运行")

    run_server()


def run_server():
    """MCP Time Server - Time and timezone conversion functionality for MCP"""
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(
        description="give a model the ability to handle time queries and timezone conversions"
    )
    parser.add_argument("--local-timezone", type=str, help="Override local timezone")

    args = parser.parse_args()

    asyncio.run(serve(args.local_timezone))


if __name__ == "__main__":
    main()
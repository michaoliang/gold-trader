# -*- coding: utf-8 -*-
"""MT5 终端路径自动检测"""
import MetaTrader5 as mt5
import os
import sys

def detect_terminal():
    """检测已安装的 MT5 终端路径"""
    candidates = []
    
    # 常见安装路径
    common_paths = [
        r"D:\MetaTrader 5 EXNESS\terminal64.exe",
        r"G:\MetaTrader 5 EXNESS\terminal64.exe",
        r"C:\Program Files\MetaTrader 5\terminal64.exe",
        r"C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
        r"D:\MetaTrader 5\terminal64.exe",
        r"G:\MT5_HJ1\terminal64.exe",
        r"G:\MT5_HJ2\terminal64.exe",
        r"G:\MT5_HJ3\terminal64.exe",
        r"G:\MT5_HJ4\terminal64.exe",
    ]
    
    # AppData 中的终端实例
    appdata = os.path.join(os.environ.get('APPDATA', ''), 'MetaQuotes', 'Terminal')
    if os.path.exists(appdata):
        for d in os.listdir(appdata):
            path = os.path.join(appdata, d, "terminal64.exe")
            if os.path.exists(path):
                # 读取 origin.txt 获取原始路径
                origin_file = os.path.join(appdata, d, "origin.txt")
                if os.path.exists(origin_file):
                    try:
                        with open(origin_file, 'r', encoding='utf-16') as f:
                            orig = f.read().strip()
                        candidates.append((orig, path))
                    except:
                        candidates.append((d, path))
                else:
                    candidates.append(("MT5_Terminal", path))
    
    # 尝试连接每个候选路径
    for name, path in candidates:
        if os.path.exists(path):
            if mt5.initialize(path):
                info = mt5.account_info()
                if info and info.login > 0:
                    print(f"找到 MT5 终端: {path}")
                    print(f"  服务器: {info.server}")
                    print(f"  登录: {info.login}")
                    print(f"  余额: ${info.balance:.2f}")
                    mt5.shutdown()
                    return path
                mt5.shutdown()
    
    # 如果都没找到，返回空
    print("未找到可用的 MT5 终端")
    return None

def write_config(terminal_path):
    """写入配置文件"""
    config = f"""[MT5]
# MT5 终端路径 (完整路径到 terminal64.exe)
terminal_path = {terminal_path}

[Alerts]
# 价格提醒阈值 (距离价位的点数)
alert_distance_points = 5

# 提醒间隔 (秒) - 同一触发点不重复提醒
alert_cooldown_sec = 120

[Target]
# 资金目标 (美元)
target_balance = 2000

[Display]
# 界面语言 (zh/en)
language = zh
"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.ini")
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write(config)
    print(f"\n配置文件已保存: {config_path}")

if __name__ == "__main__":
    path = detect_terminal()
    if path:
        write_config(path)
        print("\n配置完成! 可以运行启动脚本了。")
        sys.exit(0)
    else:
        print("\n请先安装 MetaTrader 5 终端")
        sys.exit(1)
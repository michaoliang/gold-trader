# -*- coding: utf-8 -*-
"""从 config.ini 加载配置"""
import os
import configparser

def load_config():
    """加载配置文件"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.ini")
    config = configparser.ConfigParser()
    if os.path.exists(config_path):
        config.read(config_path, encoding='utf-8')
    return config

def get_terminal_path():
    """获取 MT5 终端路径"""
    config = load_config()
    path = config.get("MT5", "terminal_path", fallback=None)
    if path and os.path.exists(path):
        return path
    # 默认尝试常见路径
    defaults = [
        r"D:\MetaTrader 5 EXNESS\terminal64.exe",
        r"G:\MetaTrader 5 EXNESS\terminal64.exe",
    ]
    for d in defaults:
        if os.path.exists(d):
            return d
    return None

def get_target_balance():
    """获取资金目标"""
    config = load_config()
    try:
        return float(config.get("Target", "target_balance", fallback="2000"))
    except:
        return 2000.0

def get_alert_cooldown():
    """获取提醒冷却时间"""
    config = load_config()
    try:
        return int(config.get("Alerts", "alert_cooldown_sec", fallback="120"))
    except:
        return 120
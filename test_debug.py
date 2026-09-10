# -*- coding: utf-8 -*-
import sys
import os

# 重定向stderr到文件以便查看错误
sys.stderr = open(r'E:\MySoftware\黄金分析工具_Portable\debug_stderr.log', 'w', encoding='utf-8')

print('Starting debug...', file=sys.stderr, flush=True)

try:
    import MetaTrader5 as mt5
    print(f'MT5 imported, version: {mt5.__version__}', file=sys.stderr, flush=True)
    
    # 测试MT5连接
    result = mt5.initialize()
    print(f'MT5 initialize: {result}', file=sys.stderr, flush=True)
    
    if result:
        acc = mt5.account_info()
        if acc:
            print(f'Account: {acc.login}, Balance: {acc.balance}', file=sys.stderr, flush=True)
        else:
            print('No account info', file=sys.stderr, flush=True)
        mt5.shutdown()
    else:
        print(f'MT5 error: {mt5.last_error()}', file=sys.stderr, flush=True)
    
    # 导入其他模块
    import numpy as np
    print(f'numpy: {np.__version__}', file=sys.stderr, flush=True)
    
    import tkinter as tk
    print('tkinter: OK', file=sys.stderr, flush=True)
    
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    print(f'matplotlib backend: {matplotlib.get_backend()}', file=sys.stderr, flush=True)
    
    # 导入主程序
    sys.path.insert(0, r'E:\MySoftware\黄金分析工具_Portable')
    print('Importing main module...', file=sys.stderr, flush=True)
    
    import 黄金分析助手
    print('Main module imported successfully', file=sys.stderr, flush=True)
    
except Exception as e:
    print(f'Error: {e}', file=sys.stderr, flush=True)
    import traceback
    traceback.print_exc(file=sys.stderr)

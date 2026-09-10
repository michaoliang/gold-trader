# -*- coding: utf-8 -*-
import sys
import traceback

# 重定向stderr
sys.stderr = open(r'E:\MySoftware\黄金分析工具_Portable\debug_full.log', 'w', encoding='utf-8')

print('=== Starting Debug ===', flush=True)

try:
    import MetaTrader5 as mt5
    print(f'MT5 version: {mt5.__version__}', flush=True)
    
    result = mt5.initialize()
    print(f'MT5 init: {result}', flush=True)
    
    if not result:
        print(f'Error: {mt5.last_error()}', flush=True)
        sys.exit(1)
    
    # 测试数据
    tick = mt5.symbol_info_tick('XAUUSDc')
    print(f'Tick: bid={tick.bid}', flush=True)
    
    rates = mt5.copy_rates_from_pos('XAUUSDc', mt5.TIMEFRAME_M1, 0, 10)
    print(f'M1 rates: {len(rates)}', flush=True)
    
    rates_h1 = mt5.copy_rates_from_pos('XAUUSDc', mt5.TIMEFRAME_H1, 0, 10)
    print(f'H1 rates: {len(rates_h1)}', flush=True)
    
    mt5.shutdown()
    print('MT5 test OK', flush=True)
    
except Exception as e:
    print(f'MT5 Error: {e}', flush=True)
    traceback.print_exc()

print('=== Importing modules ===', flush=True)

try:
    import tkinter as tk
    print('tkinter OK', flush=True)
    
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    print('matplotlib OK', flush=True)
    
    import numpy as np
    print(f'numpy: {np.__version__}', flush=True)
    
except Exception as e:
    print(f'Module Error: {e}', flush=True)
    traceback.print_exc()

print('=== Importing main module ===', flush=True)

try:
    sys.path.insert(0, r'E:\MySoftware\黄金分析工具_Portable')
    import 黄金分析助手
    print('Main module imported OK', flush=True)
    
    # 创建根窗口
    root = tk.Tk()
    print('Root window created', flush=True)
    
    # 创建应用
    app = 黄金分析助手.GoldAnalyzerApp(root)
    print('App created', flush=True)
    
    # 绑定关闭
    root.protocol("WM_DELETE_WINDOW", app._close)
    print('Protocol bound', flush=True)
    
    # 启动主循环
    print('Starting mainloop...', flush=True)
    root.mainloop()
    print('Mainloop ended', flush=True)
    
except Exception as e:
    print(f'App Error: {e}', flush=True)
    traceback.print_exc()

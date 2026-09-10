# -*- coding: utf-8 -*-
import sys
import os

# 调试输出
def dbg(msg):
    with open(r'E:\MySoftware\黄金分析工具_Portable\debug2.log', 'a', encoding='utf-8') as f:
        f.write(f"{__import__('time').strftime('%H:%M:%S')} {msg}\n")

try:
    dbg("Starting...")
    
    # 导入模块
    import MetaTrader5 as mt5
    dbg(f"MT5 imported")
    
    result = mt5.initialize()
    dbg(f"MT5 initialize: {result}")
    
    if not result:
        dbg(f"MT5 error: {mt5.last_error()}")
    
    import tkinter as tk
    from tkinter import ttk, messagebox
    dbg("tkinter imported")
    
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
    dbg("matplotlib imported")
    
    import numpy as np
    dbg(f"numpy: {np.__version__}")
    
    # 导入主程序
    sys.path.insert(0, r'E:\MySoftware\黄金分析工具_Portable')
    dbg("Importing main module...")
    
    import 黄金分析助手
    dbg("Main module imported")
    
    # 创建主窗口
    dbg("Creating root window...")
    root = tk.Tk()
    dbg(f"Root created: {root.title()}")
    
    # 创建应用
    dbg("Creating app...")
    app = 黄金分析助手.GoldAnalyzerApp(root)
    dbg("App created")
    
    # 绑定关闭事件
    root.protocol("WM_DELETE_WINDOW", app._close)
    dbg("Protocol bound")
    
    # 启动主循环
    dbg("Starting mainloop...")
    root.mainloop()
    dbg("Mainloop ended")
    
except Exception as e:
    dbg(f"Error: {e}")
    import traceback
    traceback.print_exc()

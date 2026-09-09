# -*- coding: utf-8 -*-
"""黄金分析助手 v3.0 - 完整版"""
import MetaTrader5 as mt5
import numpy as np
import threading, time, configparser, os
from datetime import datetime
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError: print('tkinter missing'); exit(1)
try:
    import matplotlib; matplotlib.use('TkAgg')
    matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei']
    matplotlib.rcParams['axes.unicode_minus'] = False
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
except ImportError: print('matplotlib not found'); exit(1)
try:
    import winsound; HAS_SOUND = True
except ImportError: HAS_SOUND = False
try:
    from win10toast import ToastNotifier; HAS_TOAST = True
except ImportError: HAS_TOAST = False

_cfg = configparser.ConfigParser()
_cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
if os.path.exists(_cfg_path): _cfg.read(_cfg_path, encoding='utf-8')

TERMINAL_PATH = _cfg.get('MT5', 'terminal_path', fallback=r'D:\MetaTrader 5 EXNESS\terminal64.exe')
TARGET_BALANCE = float(_cfg.get('Target', 'target_balance', fallback='3000'))
AUTO_MAX_POS = int(_cfg.get('AutoTrade', 'max_positions', fallback='3'))
WINDOW_WIDTH = int(_cfg.get('Window', 'width', fallback='1600'))
WINDOW_HEIGHT = int(_cfg.get('Window', 'height', fallback='800'))
REFRESH_MS = int(_cfg.get('Display', 'refresh_interval_ms', fallback='3000'))
ALERT_PCT = float(_cfg.get('Alerts', 'price_change_pct', fallback='1.0'))
ALERT_CD = int(_cfg.get('Alerts', 'cooldown_sec', fallback='120'))

def _dbg(msg):
    try:
        with open(r'E:\MySoftware\黄金分析工具_Portable\debug.log', 'a', encoding='utf-8') as f:
            f.write(f'{msg}\n')
    except: pass
    def _panel_prices(self, parent):
        f = self._frame(parent, "实时行情")
        for sym, name in MT5Engine.SYMBOLS.items():
            row = tk.Frame(f, bg=self.C["card"])
            row.pack(fill="x", padx=4, pady=2)
            kf = tk.Frame(row, bg=self.C["card"])
            kf.pack(side="left")
            tk.Label(kf, text=sym, font=("Consolas", 9, "bold"), fg=self.C["accent"], bg=self.C["card"]).pack(side="left")
            tk.Label(kf, text=name, font=("Consolas", 8), fg=self.C["dim"], bg=self.C["card"]).pack(side="left", padx=(4, 0))
            vv = tk.StringVar(value="--")
            self.price_vars[sym] = vv
            tk.Label(row, textvariable=vv, font=("Consolas", 10, "bold"), fg=self.C["accent"], bg=self.C["card"]).pack(side="right", padx=(10, 0))
            dv = tk.StringVar(value="--")
            self.daily_vars[sym] = dv
            tk.Label(row, textvariable=dv, font=("Consolas", 8), fg=self.C["yellow"], bg=self.C["card"]).pack(side="right", padx=(0, 4))
            cl = tk.Frame(row, width=8, height=8, bg=self.C["bg"])
            cl.pack(side="right", padx=4)
            self.pcl[sym] = cl

    def _panel_signal(self, parent):
        f = self._frame(parent, "信号分析")
        tk.Label(f, textvariable=self.sl, font=("Consolas", 11, "bold"), fg=self.C["yellow"], bg=self.C["card"]).pack(pady=(0, 4))
        tf = tk.Frame(f, bg=self.C["card"]); tf.pack(fill="x")
        for opt in ["M1","M5","M6","M15","M30","H1","H4","D1"]:
            tk.Button(tf, text=opt, font=("Consolas", 8, "bold"), fg=self.C["accent"], bg=self.C["card"], highlightthickness=1, highlightcolor=self.C["bd"],
                      activebackground=self.C["accent"], relief="flat", cursor="hand2",
                      command=lambda o=opt: self.tv.set(o) or self._signal() or self._chart()).pack(side="left", padx=2)
        self.sd = tk.Text(f, height=8, font=("Consolas", 9), fg=self.C["tx"], bg=self.C["card"],
                          insertbackground=self.C["tx"], relief="flat", state="disabled")
        self.sd.pack(fill="x", padx=4, pady=(4, 0))
        qf = tk.Frame(f, bg=self.C["card"]); qf.pack(fill="x", padx=4, pady=(4,0))
        tk.Label(qf, text="快捷交易:", font=("Consolas", 9), fg=self.C["dim"], bg=self.C["card"]).pack(side="left")
        self.quick_lot_var = tk.DoubleVar(value=0.01)
        tk.Spinbox(qf, from_=0.01, to=2.0, increment=0.01, textvariable=self.quick_lot_var, width=6,
                 font=("Consolas", 9), bg=self.C["bg"], fg=self.C["tx"], relief="flat").pack(side="left", padx=(0,4))
        tk.Button(qf, text="买入", font=("Consolas", 9, "bold"), fg="white", bg=self.C["green"], relief="flat", cursor="hand2",
                 command=lambda: self._quick_trade("buy")).pack(side="left", padx=2)
        tk.Button(qf, text="卖出", font=("Consolas", 9, "bold"), fg="white", bg=self.C["red"], relief="flat", cursor="hand2",
                 command=lambda: self._quick_trade("sell")).pack(side="left", padx=2)

    def _panel_account(self, parent):
        f = self._frame(parent, "账户信息")
        grid = tk.Frame(f, bg=self.C["card"]); grid.pack(fill="x", padx=6)
        for i, (k, lbl) in enumerate([('bal','余额'),('eq','权益'),('mg','保证金'),('free','可用'),('prof','盈亏')]):
            tk.Label(grid, text=lbl, font=("Consolas", 9), fg=self.C["dim"], bg=self.C["card"]).grid(row=i//3, column=i%3, sticky="w", padx=(0,4))
            self.avars[k] = tk.StringVar(value="--")
            tk.Label(grid, textvariable=self.avars[k], font=("Consolas", 9), fg=self.C["tx"], bg=self.C["card"]).grid(row=i//3, column=i%3, sticky="e")
        self.plbl = tk.Label(f, text="无持仓", font=("Consolas", 9), fg=self.C["dim"], bg=self.C["card"])
        self.plbl.pack(pady=(4, 0))
        self.pt = tk.Text(f, height=3, font=("Consolas", 9), fg=self.C["tx"], bg=self.C["card"], relief="flat", state="disabled")
        self.pt.pack(fill="x", padx=4, pady=(0, 4))

    def _panel_chart(self, parent):
        f = self._frame(parent, "K线图表")
        tf = tk.Frame(f, bg=self.C["card"]); tf.pack(fill="x")
        self.chart_tv = tk.StringVar(value="H1")
        for opt in ["M1","M5","M6","M15","M30","H1","H4","D1"]:
            tk.Button(tf, text=opt, font=("Consolas", 8, "bold"), fg=self.C["accent"], bg=self.C["card"], highlightthickness=1, highlightcolor=self.C["bd"],
                      activebackground=self.C["accent"], relief="flat", cursor="hand2",
                      command=lambda o=opt: self.chart_tv.set(o) or self.tv.set(o) or self._chart() or self._signal()).pack(side="left", padx=2)
        self.fig = Figure(figsize=(10, 5), facecolor=self.C["card"])
        self.canvas = FigureCanvasTkAgg(self.fig, master=f)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _panel_indicators(self, parent):
        f = self._frame(parent, "技术指标")
        grid = tk.Frame(f, bg=self.C["card"]); grid.pack(fill="x", padx=6)
        items = [('MA5',self.ivars['ma5']),('MA10',self.ivars['ma10']),('MA20',self.ivars['ma20']),('MA50',self.ivars['ma50']),
                 ('RSI',self.ivars['rsi']),('MACD',self.ivars['macd']),('布林上',self.ivars['bbu']),('布林下',self.ivars['bbl']),('ATR',self.ivars['atr']),('波动',self.vv)]
        for i, (lbl, var) in enumerate(items):
            tk.Label(grid, text=lbl, font=("Consolas", 9), fg=self.C["dim"], bg=self.C["card"]).grid(row=i//5, column=i%5, sticky="w", padx=(0,4))
            tk.Label(grid, textvariable=var, font=("Consolas", 9), fg=self.C["accent"], bg=self.C["card"]).grid(row=i//5, column=i%5, sticky="e")
    def _panel_alerts(self, parent):
        f = self._frame(parent, "价格预警")
        af = tk.Frame(f, bg=self.C["card"]); af.pack(fill="x", padx=8)
        tk.Label(af, text="波动阈值 %:", font=("Consolas", 9), fg=self.C["dim"], bg=self.C["card"]).pack(side="left", padx=(0,4))
        tk.Spinbox(af, from_=0.5, to=10, increment=0.5, textvariable=self.alert_pct, width=5,
                   font=("Consolas", 9), bg=self.C["bg"], fg=self.C["tx"], relief="flat").pack(side="left", padx=(0,8))
        tk.Button(af, text="添加预警", command=self._add_alert,
                  bg=self.C["accent"], fg=self.C["bg"], font=("Consolas", 9), cursor="hand2", relief="flat", width=8).pack(side="left")
        nf = tk.Frame(f, bg=self.C["card"]); nf.pack(fill="x", padx=8, pady=(4,0))
        self.notify_popup_var = tk.BooleanVar(value=True)
        self.notify_sound_var = tk.BooleanVar(value=True)
        tk.Checkbutton(nf, text="桌面弹窗通知", variable=self.notify_popup_var,
                       bg=self.C["card"], fg=self.C["tx"], selectcolor=self.C["bd"],
                       activebackground=self.C["card"], activeforeground=self.C["tx"],
                       font=("Consolas", 9)).pack(side="left", padx=(0,15))
        tk.Checkbutton(nf, text="声音告警", variable=self.notify_sound_var,
                       bg=self.C["card"], fg=self.C["tx"], selectcolor=self.C["bd"],
                       activebackground=self.C["card"], activeforeground=self.C["tx"],
                       font=("Consolas", 9)).pack(side="left")
        self.alert_list = tk.Listbox(f, height=5, font=("Consolas", 9),
                                     fg=self.C["tx"], bg=self.C["bg"],
                                     selectbackground=self.C["bd"], selectforeground=self.C["tx"],
                                     relief="flat", activestyle="none")
        self.alert_list.pack(fill="both", expand=True, padx=8, pady=(0,5))
        self.alert_list.insert(0, "XAUUSDc 黄金  预警阈值 1.0%")

    def _panel_auto_trade(self, parent):
        f = self._frame(parent, "自动交易")
        tf = tk.Frame(f, bg=self.C["card"]); tf.pack(fill="x", padx=8)
        tk.Label(tf, text="自动交易:", font=("Consolas", 9), fg=self.C["dim"], bg=self.C["card"]).pack(side="left", padx=(0,8))
        self.auto_on_var = tk.BooleanVar(value=False)
        tk.Checkbutton(tf, variable=self.auto_on_var, command=self._toggle_auto,
                       bg=self.C["card"], fg=self.C["tx"], selectcolor=self.C["accent"], font=("Consolas", 9)).pack(side="left")
        self.auto_status_var = tk.StringVar(value="已停止")
        tk.Label(tf, textvariable=self.auto_status_var, font=("Consolas", 9), fg=self.C["yellow"], bg=self.C["card"]).pack(side="left", padx=(10,0))
        lf = tk.Frame(f, bg=self.C["card"]); lf.pack(fill="x", padx=8, pady=(4,0))
        tk.Label(lf, text="手数:", font=("Consolas", 9), fg=self.C["dim"], bg=self.C["card"]).pack(side="left", padx=(0,4))
        tk.Spinbox(lf, from_=0.01, to=2.0, increment=0.01, textvariable=self.auto_lot_var, width=6,
                   font=("Consolas", 9), bg=self.C["bg"], fg=self.C["tx"], relief="flat").pack(side="left", padx=(0,15))
        tk.Label(lf, text="RSI买入<", font=("Consolas", 9), fg=self.C["dim"], bg=self.C["card"]).pack(side="left", padx=(0,4))
        tk.Spinbox(lf, from_=10, to=50, increment=1, textvariable=self.auto_rsi_buy_var, width=4,
                   font=("Consolas", 9), bg=self.C["bg"], fg=self.C["tx"], relief="flat").pack(side="left", padx=(0,10))
        tk.Label(lf, text="RSI卖出>", font=("Consolas", 9), fg=self.C["dim"], bg=self.C["card"]).pack(side="left", padx=(0,4))
        tk.Spinbox(lf, from_=50, to=90, increment=1, textvariable=self.auto_rsi_sell_var, width=4,
                   font=("Consolas", 9), bg=self.C["bg"], fg=self.C["tx"], relief="flat").pack(side="left", padx=(0,15))
        self.auto_log = tk.Text(f, height=5, font=("Consolas", 9), fg=self.C["tx"], bg=self.C["card"], relief="flat", state="disabled")
        self.auto_log.pack(fill="both", expand=True, padx=8, pady=(4,0))

    def _panel_ea(self, parent):
        f = self._frame(parent, "EA控制")
        ptf = tk.Frame(f, bg=self.C['card']); ptf.pack(fill='x', padx=8, pady=(4,0))
        tk.Label(ptf, text='MT5路径:', font=('Consolas', 9), fg=self.C['dim'], bg=self.C['card']).pack(side='left', padx=(0,4))
        self.ea_mt5_path_var = tk.StringVar(value=r'D:\MetaTrader 5 EXNESS')
        tk.Entry(ptf, textvariable=self.ea_mt5_path_var, font=('Consolas', 9),
                 bg=self.C['bg'], fg=self.C['tx'], relief='flat', width=45).pack(side='left', fill='x', expand=True, padx=(0,4))
        tk.Button(ptf, text='选择', command=self._select_mt5_path,
                  bg=self.C['card'], fg=self.C['accent'], font=('Consolas', 9),
                  cursor='hand2', relief='flat').pack(side='left', padx=2)
        bf = tk.Frame(f, bg=self.C['card']); bf.pack(fill='x', padx=8, pady=4)
        tk.Label(bf, text='EA状态:', font=('Consolas', 9), fg=self.C['dim'], bg=self.C['card']).pack(side='left', padx=(0,8))
        self.ea_status_var = tk.StringVar(value='未部署')
        tk.Label(bf, textvariable=self.ea_status_var, font=('Consolas', 9), fg=self.C['yellow'], bg=self.C['card']).pack(side='left', padx=(0,15))
        tk.Button(bf, text='编译部署EA', command=self._deploy_ea,
                  bg=self.C['accent'], fg=self.C['bg'], font=('Consolas', 9, 'bold'),
                  cursor='hand2', relief='flat', width=12).pack(side='left', padx=2)
        inf = tk.Frame(f, bg=self.C['card']); inf.pack(fill='x', padx=8, pady=(4,0))
        tk.Label(inf, text='1.选择MT5路径 -> 2.编译部署 -> 3.打开MT5 -> 4.导航窗口拖EA到图表 -> 5.勾选允许算法交易',
                 font=('Consolas', 8), fg=self.C['dim'], bg=self.C['card'], wraplength=500).pack(anchor='w')
        self._check_ea_status()

    def _panel_backtest(self, parent):
        f = self._frame(parent, "历史回测 (MA交叉+RSI过滤)")
        tf = tk.Frame(f, bg=self.C["card"]); tf.pack(fill="x", padx=8)
        tk.Label(tf, text="周期:", font=("Consolas", 9), fg=self.C["dim"], bg=self.C["card"]).pack(side="left", padx=(0,4))
        bt_tf = tk.StringVar(value="H1")
        for opt in ["M15","M30","H1","H4"]:
            tk.Radiobutton(tf, text=opt, variable=bt_tf, value=opt, bg=self.C["card"], fg=self.C["tx"], selectcolor=self.C["bd"]).pack(side="left", padx=4)
        tk.Button(tf, text="执行回测", command=lambda: self._run_backtest(bt_tf),
                  bg=self.C["accent"], fg=self.C["bg"], font=("Consolas", 9), cursor="hand2", relief="flat", width=8).pack(side="left", padx=8)
        self.bt_result = tk.Text(f, height=8, font=("Consolas", 9), fg=self.C["tx"], bg=self.C["card"], relief="flat", state="disabled")
        self.bt_result.pack(fill="x", padx=8, pady=(4, 0))
    def _refresh(self):
        if self.stop: return
        if not self.anz.ok:
            self._update_conn()
            if not self.anz._connecting:
                import time as _t
                if not hasattr(self, "_last_reconnect") or _t.time() - self._last_reconnect > 10:
                    self._last_reconnect = _t.time()
                    self.anz.connect()
            self.root.after(REFRESH_MS, self._refresh)
            return
        try:
            for sym, name in MT5Engine.SYMBOLS.items():
                t = self.anz.tick(sym)
                if t:
                    dig = self.anz._sym_digits.get(sym, 2)
                    prev = self._prev.get(sym)
                    if prev:
                        ch = t.bid - prev
                        pct = ch / prev * 100 if prev else 0
                        sg = "+" if ch >= 0 else ""
                        co = self.C["green"] if ch >= 0 else self.C["red"]
                        self.pcl[sym].config(bg=co)
                        self.price_vars[sym].set(f"{t.bid:.{dig}f}  {sg}{pct:.2f}%")
                    else:
                        self.price_vars[sym].set(f"{t.bid:.{dig}f}")
                    self._prev[sym] = t.bid
                    pc = self._prev_close.get(sym)
                    if pc:
                        dch = t.bid - pc
                        dpct = dch / pc * 100
                        dsg = "+" if dch >= 0 else ""
                        dco = self.C["green"] if dch >= 0 else self.C["red"]
                        self.daily_vars[sym].set(f"[日{dsg}{dpct:.2f}%]")
                        self.daily_vars[sym].config(fg=dco)
            self._signal()
            self._account()
            self._chart()
            self._check_alerts()
            if self.auto_on: self._auto_trade_step()
            self._check_ea_status()
        except Exception as e:
            _dbg(f"_refresh error: {e}")
        self._update_conn()
        self.root.after(REFRESH_MS, self._refresh)

    def _check_alerts(self):
        try:
            result = self.alert_system.check("XAUUSDc", engine=self.anz)
            if result:
                msg = f"黄金波动 {result['chg']:.2f}% @ "
                if self.notify_popup_var.get() and HAS_TOAST:
                    try: self.notifier.show_toast("价格预警", msg, duration=5)
                    except: pass
                if self.notify_sound_var.get() and HAS_SOUND:
                    try: winsound.Beep(800, 200)
                    except: pass
                self._auto_log(f"预警: {msg}")
        except Exception: pass

    def _start_refresh(self):
        self._prev = {}
        self._prev_close = {}
        for sym in MT5Engine.SYMBOLS.keys():
            pc = self.anz.prev_close(sym)
            if pc is not None: self._prev_close[sym] = pc
            else:
                t = self.anz.tick(sym)
                if t: self._prev[sym] = t.bid
        self._target(); self._refresh()

    def _close(self):
        self.stop = True; self.anz.shutdown(); self.root.destroy()

    def _update_conn(self):
        if self.anz.ok:
            acc = self.anz.account()
            self.conn_var.set("已连接" if acc else "MT5运行中")
            self.conn_lbl.config(fg=self.C["green"])
        else:
            self.conn_var.set("MT5未连接 - 等待恢复")
            self.conn_lbl.config(fg=self.C["red"])

    def _target(self):
        i = self.anz.account()
        if i:
            rem = TARGET_BALANCE - i["balance"]
            done = chr(27700) + chr(36229) + chr(25104) + chr(25104)
            self.target_var.set(f"目标 ${TARGET_BALANCE:.0f} | 当前 ${i['balance']:.0f} | {done if i['balance'] >= TARGET_BALANCE else '还需 +$' + str(int(rem))}")
    def _signal(self):
        a = self.anz.analyze("XAUUSDc", self.tv.get())
        if not a: return
        txt, col = a["overall"]
        cm = {"green": self.C["green"], "red": self.C["red"], "orange": self.C["yellow"], "lightgreen": self.C["green"], "gray": self.C["dim"]}
        if self.sl_label: self.sl_label.config(text=txt, fg=cm.get(col, self.C["yellow"]))
        else: self.sl.set(txt)
        d = f"Trend: {a['trend']}\nScore: Buy {a['bs']} | Sell {a['ss']}\n"
        if a["sup"]: d += f"Support: ${a['sup']:.1f}  Resistance: ${a['res']:.1f}\n"
        d += "\n"
        for n, l in a["sig"]:
            lc = self.C["green"] if l in ("买入", "偏多", "强势") else (self.C["red"] if l in ("卖出", "偏空", "强势") else self.C["yellow"])
            d += f"* {n}: {l}\n"
        self.sd.config(state="normal"); self.sd.delete("1.0", "end"); self.sd.insert("1.0", d); self.sd.config(state="disabled")
        self.ivars["ma5"].set(f"{a['ma']['5']:.2f}")
        self.ivars["ma10"].set(f"{a['ma']['10']:.2f}")
        self.ivars["ma20"].set(f"{a['ma']['20']:.2f}")
        self.ivars["ma50"].set(f"{a['ma']['50']:.2f}")
        self.ivars["rsi"].set(f"{a['rsi']:.1f}")
        self.ivars["macd"].set(f"{a['macd']:.2f}")
        if a["bb"]:
            self.ivars["bbu"].set(f"{a['bb'][0]:.2f}")
            self.ivars["bbl"].set(f"{a['bb'][2]:.2f}")
        self.ivars["atr"].set(f"{a['atr']:.2f}")
        self.vv.set(f"{a['atr'] / a['price'] * 100:.2f}% ({a['vol']})")

    def _account(self):
        try:
            i = self.anz.account()
            if not i: return
            for k, short in [("balance","bal"),("equity","eq"),("margin","mg"),("free","free")]:
                self.avars[short].set("${:,.2f}".format(i[k]))
            p = i["profit"]
            self.avars["prof"].set("${:+,.2f}".format(p))
            self.plbl.config(fg=self.C["green"] if p >= 0 else self.C["red"])
            pos = mt5.positions_get(symbol="XAUUSDc")
            ps = list(pos) if pos is not None and len(pos) > 0 else []
            txt = ""
            if ps:
                tick = mt5.symbol_info_tick("XAUUSDc")
                if tick:
                    for p in ps:
                        d = "SELL" if p.type == mt5.POSITION_TYPE_SELL else "BUY"
                        pnl = (tick.bid - p.price_open) * p.volume * 100 if p.type == mt5.POSITION_TYPE_BUY else (p.price_open - tick.bid) * p.volume * 100
                        st = "盈" if pnl >= 0 else "亏"
                        txt += f"{d} {p.volume:.2f}@{p.price_open:.2f} {st}${abs(pnl):.0f}\n"
                else: txt = "行情数据获取失败"
            else: txt = "无持仓"
            self.pt.config(state="normal")
            self.pt.delete("1.0", "end")
            self.pt.insert("1.0", txt)
            self.pt.config(state="disabled")
            self.plbl.config(text="有持仓" if ps else "无持仓", fg=self.C["green"] if ps else self.C["dim"])
        except Exception as e:
            self.pt.config(state="normal")
            self.pt.delete("1.0", "end")
            self.pt.insert("1.0", "持仓获取错误: " + str(e))
            self.pt.config(state="disabled")

    def _chart(self):
        self.fig.clear(); a = self.anz.analyze("XAUUSDc", self.tv.get())
        if not a or a.get("rates") is None: return
        r = a["rates"]; n = min(len(r), 80)
        ti = np.arange(n); cl = r[-n:]["c"]; op = r[-n:]["o"]
        hi = r[-n:]["h"]; lo = r[-n:]["l"]
        m5 = np.convolve(cl, np.ones(5)/5, mode="valid")
        m10 = np.convolve(cl, np.ones(10)/10, mode="valid")
        m20 = np.convolve(cl, np.ones(20)/20, mode="valid")
        ax = self.fig.add_subplot(111); ax.set_facecolor(self.C["card"])
        for i in range(n):
            co = self.C["red"] if cl[i] >= op[i] else self.C["green"]
            ax.plot([ti[i], ti[i]], [lo[i], hi[i]], color=co, linewidth=0.8)
            ax.add_patch(Rectangle((ti[i]-0.3, min(cl[i], op[i])), 0.6, abs(cl[i]-op[i]), facecolor=co, edgecolor=co))
        o = n - len(m5); ax.plot(ti[o:], m5, "white", linewidth=1, label="MA5")
        o = n - len(m10); ax.plot(ti[o:], m10, "orange", linewidth=1, label="MA10")
        o = n - len(m20); ax.plot(ti[o:], m20, "blue", linewidth=1, label="MA20")
        if a["sup"]: ax.axhline(y=a["sup"], color="green", linestyle="--", alpha=0.5, label="支撑")
        if a["res"]: ax.axhline(y=a["res"], color="red", linestyle="--", alpha=0.5, label="阻力")
        ax.set_title(f"XAUUSDc {self.tv.get()}  当前: {a['price']:.2f}", color=self.C["tx"], fontsize=10)
        ax.tick_params(colors=self.C["dim"])
        for sp in ax.spines.values(): sp.set_color(self.C["bd"])
        ax.legend(loc="upper left", facecolor=self.C["card"], edgecolor=self.C["bd"], labelcolor=self.C["tx"])
        self.fig.tight_layout(); self.canvas.draw()
    def _select_mt5_path(self):
        import tkinter.filedialog as fd
        path = fd.askdirectory(title='选择MT5终端目录')
        if path: self.ea_mt5_path_var.set(path); self._check_ea_status()

    def _deploy_ea(self):
        import subprocess, os, shutil
        mt5_dir = self.ea_mt5_path_var.get()
        src_ea = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MQL5', 'Experts', 'GoldTrader_MTF_EA.mq5')
        dst_ea = os.path.join(mt5_dir, 'MQL5', 'Experts', 'GoldTrader_MTF_EA.mq5')
        if not os.path.exists(src_ea): self.ea_status_var.set('源码不存在'); return
        os.makedirs(os.path.dirname(dst_ea), exist_ok=True)
        shutil.copy2(src_ea, dst_ea)
        editor = os.path.join(mt5_dir, 'MetaEditor64.exe')
        if os.path.exists(editor):
            result = subprocess.run([editor, '/compile:' + dst_ea, '/log'], capture_output=True, text=True, timeout=120)
            if result.returncode == 0 and '0 errors' in result.stdout: self.ea_status_var.set('已部署(最新)')
            else: self.ea_status_var.set('编译失败')
        else: self.ea_status_var.set('未找到编译器')

    def _check_ea_status(self):
        ea_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MQL5', 'Experts', 'GoldTrader_MTF_EA.ex5')
        if os.path.exists(ea_file):
            import time; age = time.time() - os.path.getmtime(ea_file)
            self.ea_status_var.set('已部署(最新)' if age < 3600 else '已部署')
        else: self.ea_status_var.set('未部署')

    def _toggle_auto(self):
        self.auto_on = self.auto_on_var.get()
        if self.auto_on: self.auto_status_var.set("运行中"); self._auto_log("已开启自动交易")
        else: self.auto_status_var.set("已停止"); self._auto_log("已关闭自动交易")

    def _auto_log(self, msg):
        self.auto_log.config(state="normal")
        self.auto_log.insert("end", f"{datetime.now().strftime('%H:%M:%S')} {msg}\n")
        self.auto_log.see("end")
        self.auto_log.config(state="disabled")

    def _add_alert(self):
        pct = self.alert_pct.get()
        self.alert_list.insert("end", f"XAUUSDc 黄金  预警阈值 {pct:.1f}%")
        self.alert_system.add("XAUUSDc", threshold_pct=pct)

    def _run_backtest(self, tf_var):
        tf = tf_var.get()
        self.bt_result.config(state="normal"); self.bt_result.delete("1.0", "end")
        self.bt_result.insert("1.0", "回测中..."); self.bt_result.config(state="disabled")
        threading.Thread(target=self._do_backtest, args=(tf,), daemon=True).start()

    def _do_backtest(self, tf):
        r = self.anz.backtest("XAUUSDc", tf)
        if r is None: txt = "数据不足，无法回测"
        else:
            txt = f"周期: {tf} | 初始资金: ${r['initial_capital']:,.0f}\n"
            txt += f"最终资金: ${r['final_capital']:,.0f}  收益: ${r['total_return']:+.2f}%\n"
            txt += f"交易次数: {r['total_trades']} | 胜率: {r['win_rate']:.1f}%\n"
            txt += f"盈亏比: {r['profit_factor']:.2f}"
        self.bt_result.config(state="normal")
        self.bt_result.delete("1.0", "end")
        self.bt_result.insert("1.0", txt); self.bt_result.config(state="disabled")

    def _quick_trade(self, action):
        try:
            lot = self.quick_lot_var.get()
            sym = "XAUUSDc"
            res = self.anz.order_send(sym, action, lot)
            if res and res.retcode == 0:
                co = self.C["red"] if action == "buy" else self.C["green"]
                txt = f"{action.upper()} {lot}手 @ {sym}\n"
                self.sd.config(state="normal")
                self.sd.insert("end", txt)
                self.sd.config(state="disabled", fg=co)
            else:
                err = res.error if res else "未知错误"
                self._auto_log(f"交易失败: {err}")
        except Exception as _e: self._auto_log(f"交易错误: {str(_e)[:50]}")

    def _auto_trade_step(self):
        try:
            if not self.auto_on: return
            acc = self.anz.account()
            if not acc: return
            if acc["balance"] >= TARGET_BALANCE:
                self.auto_on = False; self.auto_status_var.set("目标达成!")
                self._auto_log(f"恭喜! 达到目标 ${TARGET_BALANCE:.0f}"); return
            pos = self.anz.positions("XAUUSDc")
            if pos and len(pos) >= AUTO_MAX_POS: return
            h1 = self.anz.analyze("XAUUSDc", "H1")
            m5 = self.anz.analyze("XAUUSDc", "M5")
            tick = self.anz.tick("XAUUSDc")
            if not h1 or not m5 or not tick: return
            lot = self.auto_lot_var.get(); price = tick.bid
            if h1["trend"] in ("强势上涨", "偏多") and m5["rsi"] < self.auto_rsi_buy_var.get():
                has_buy = any(p.type == mt5.POSITION_TYPE_BUY for p in (pos or []))
                if not has_buy:
                    sl = price * 0.98; tp = price * 1.04
                    res = self.anz.order_send("XAUUSDc", "buy", lot, sl=sl, tp=tp)
                    if res and res.retcode == 0: self._auto_log(f"买入 {lot}手 @{price:.2f}")
            elif h1["trend"] in ("强势下跌", "偏空") and m5["rsi"] > self.auto_rsi_sell_var.get():
                has_sell = any(p.type == mt5.POSITION_TYPE_SELL for p in (pos or []))
                if not has_sell:
                    sl = price * 1.02; tp = price * 0.96
                    res = self.anz.order_send("XAUUSDc", "sell", lot, sl=sl, tp=tp)
                    if res and res.retcode == 0: self._auto_log(f"卖出 {lot}手 @{price:.2f}")
            if pos:
                for p in pos:
                    pnl = (price - p.price_open) * p.volume * 100 if p.type == mt5.POSITION_TYPE_BUY else (p.price_open - price) * p.volume * 100
                    if pnl > 50:
                        close_act = "sell" if p.type == mt5.POSITION_TYPE_BUY else "buy"
                        res = self.anz.order_send("XAUUSDc", close_act, p.volume)
                        if res and res.retcode == 0: self._auto_log(f"止盈平仓 ${pnl:+.0f}")
        except Exception: pass


if __name__ == "__main__":
    root = tk.Tk()
    app = GoldAnalyzerApp(root)
    root.protocol("WM_DELETE_WINDOW", app._close)
    root.mainloop()

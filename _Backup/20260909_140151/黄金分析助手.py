import MetaTrader5 as mt5
import numpy as np
import threading
import time
from datetime import datetime
from collections import deque

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    print("tkinter missing"); exit(1)

try:
    import matplotlib
    matplotlib.use('TkAgg')
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    from matplotlib.patches import Rectangle
except ImportError:
    print("matplotlib missing"); exit(1)


class MT5Engine:
    SYMBOLS = {
        "XAUUSDc": "\u9ec4\u91d1",
        "EURUSDc": "\u6b27\u5143/\u7f8e\u5143",
        "USDJPYc": "\u7f8e\u5143/\u65e5\u5143",
        "BTCUSDc": "\u6bd4\u7279\u5e01",
    }
    TF_MAP = {'M1':mt5.TIMEFRAME_M1,'M5':mt5.TIMEFRAME_M5,'M15':mt5.TIMEFRAME_M15,
              'M30':mt5.TIMEFRAME_M30,'H1':mt5.TIMEFRAME_H1,'H4':mt5.TIMEFRAME_H4,'D1':mt5.TIMEFRAME_D1}

    def __init__(self):
        self.ok = mt5.initialize()
        self._connecting = False
        self._sym_digits = {}

    def shutdown(self):
        if self.ok: mt5.shutdown()

    def tick(self, s):
        return mt5.symbol_info_tick(s) if self.ok else None

    def rates(self, s, tf, n=100):
        if not self.ok: return None
        r = mt5.copy_rates_from_pos(s, self.TF_MAP.get(tf, mt5.TIMEFRAME_H1), 0, n)
        return np.array([(x['time'],x['open'],x['high'],x['low'],x['close'],x['tick_volume'])
                        for x in r], dtype=[('time','i8'),('open','f8'),('high','f8'),('low','f8'),('close','f8'),('tick_volume','i8')]) if r else None

    def account(self):
        i = mt5.account_info()
        return {'balance':i.balance,'equity':i.equity,'margin':i.margin,
                'free':i.margin_free,'profit':i.profit,'lev':i.leverage} if i else None

    def positions(self, s=None):
        p = mt5.positions_get(symbol=s) if s else mt5.positions_get()
        return list(p) if p else []

    def order(self, sym, act, lot, sl=0, tp=0):
        t = self.tick(sym)
        if not t: return None
        pr = t.ask if act=='buy' else t.bid
        ot = mt5.ORDER_TYPE_BUY if act=='buy' else mt5.ORDER_TYPE_SELL
        req = {"action":mt5.TRADE_ACTION_DEAL,"symbol":sym,"volume":lot,"type":ot,
               "price":pr,"sl":sl,"tp":tp,"deviation":20,"magic":20260908,
               "comment":"GoldAnalyzer","type_time":mt5.ORDER_TIME_GTC,
               "type_filling":mt5.ORDER_FILLING_IOC}
        return mt5.order_send(req)

    # ---- indicators ----
    def ma(self, c, p):
        return np.mean(c[-p:]) if len(c)>=p else np.mean(c)

    def rsi(self, c, p=14):
        if len(c)<p+1: return 50.0
        d = np.diff(c[-p-1:])
        g = np.mean(np.where(d>0,d,0))
        l = np.mean(np.where(d<0,-d,0))
        return 100-(100/(1+g/l)) if l>0 else 100

    def macd(self, c, f=12, s=26):
        if len(c)<s: return 0,0,0
        m = np.mean(c[-f:])-np.mean(c[-s:])
        return m, m*0.9, m*0.1

    def bb(self, c, p=20, k=2):
        if len(c)<p: return None
        m = np.mean(c[-p:]); sd = np.std(c[-p:])
        return m+k*sd, m, m-k*sd

    def atr(self, h, l, c, p=14):
        if len(h)<p+1: return 0
        tr = [max(h[i]-l[i], abs(h[i]-c[i-1]), abs(l[i]-c[i-1])) for i in range(-p,0)]
        return np.mean(tr)

    def levels(self, rates):
        if rates is None or len(rates)<20: return None, None
        h = rates['high']; l = rates['low']
        resist, supp = [], []
        for i in range(5, len(h)-5):
            if h[i] == max(h[i-5:i+6]): resist.append(h[i])
            if l[i] == min(l[i-5:i+6]): supp.append(l[i])
        return max(resist) if resist else None, min(supp) if supp else None

    def analyze(self, sym='XAUUSDc', tf='H1'):
        r = self.rates(sym, tf, 100)
        if r is None or len(r) == 0: return None
        c,h,l = r['close'],r['high'],r['low']
        t = self.tick(sym)
        if not t: return None
        ma = {p:self.ma(c,p) for p in [5,10,20,50]}
        rsi = self.rsi(c)
        m, ms, mh = self.macd(c)
        bb = self.bb(c)
        atr = self.atr(h,l,c)
        res, sup = self.levels(r)
        sig, trend = [], ""
        if ma[5]>ma[10]>ma[20]: trend,sig="Strong Up",[("MA Bullish","Strong")]
        elif ma[5]<ma[10]<ma[20]: trend,sig="Strong Down",[("MA Bearish","Strong")]
        elif ma[5]>ma[10]: trend,sig="Bullish",[("MA Up","Neutral")]
        elif ma[5]<ma[10]: trend,sig="Bearish",[("MA Down","Neutral")]
        if rsi>70: sig.append((f"RSI={rsi:.0f} Overbought","Sell"))
        elif rsi<30: sig.append((f"RSI={rsi:.0f} Oversold","Buy"))
        elif rsi>60: sig.append((f"RSI={rsi:.0f}","Bearish"))
        elif rsi<40: sig.append((f"RSI={rsi:.0f}","Bullish"))
        else: sig.append((f"RSI={rsi:.0f}","Neutral"))
        if m>0 and mh>0: sig.append(("MACD Cross Up","Buy"))
        elif m<0 and mh<0: sig.append(("MACD Cross Down","Sell"))
        if bb and t.bid<bb[2]: sig.append(("Below BB Lower","Buy"))
        elif bb and t.bid>bb[0]: sig.append(("Above BB Upper","Sell"))
        if sup and t.bid-sup<2: sig.append((f"Support ${sup:.1f}","Watch"))
        if res and res-t.bid<2: sig.append((f"Resistance ${res:.1f}","Watch"))
        ap = atr/t.bid*100 if t.bid>0 else 0
        vl = "High" if ap>0.5 else ("Medium" if ap>0.2 else "Low")
        bs = sum(1 for x in sig if x[1] in ("Buy","Bullish","Strong"))
        ss = sum(1 for x in sig if x[1] in ("Sell","Bearish","Strong"))
        if bs>ss+2: ov=("STRONG BUY","green")
        elif bs>ss: ov=("BULLISH","lightgreen")
        elif ss>bs+2: ov=("STRONG SELL","red")
        elif ss>bs: ov=("BEARISH","orange")
        else: ov=("NEUTRAL","gray")
        return {'sym':sym,'name':self.SYMBOLS.get(sym,sym),'price':t.bid,'ask':t.ask,
                'spread':t.ask-t.bid,'trend':trend,'ma':ma,'rsi':rsi,'macd':m,
                'bb':bb,'atr':atr,'atr_pct':ap,'vol':vl,'signals':sig,'overall':ov,
                'bs':bs,'ss':ss,'res':res,'sup':sup,'closes':c,'rates':r}



    def connect(self):
        if getattr(self, "_connecting", False): return
        self._connecting = True
        try:
            self.ok = mt5.initialize()
            if self.ok:
                for sym in self.SYMBOLS:
                    si = mt5.symbol_info(sym)
                    if si:
                        self._sym_digits[sym] = si.digits if hasattr(si, "digits") else 2
                self._connecting = False
        except Exception:
            self._connecting = False

    def prev_close(self, sym):
        try:
            r = mt5.copy_rates_from_pos(sym, mt5.TIMEFRAME_D1, 1, 1)
            return r[0]["close"] if r and len(r) > 0 else None
        except:
            return None

    def order_send(self, sym, act, lot, sl=0, tp=0):
        t = self.tick(sym)
        if not t: return None
        price = t.ask if act == "buy" else t.bid
        ot = mt5.ORDER_TYPE_BUY if act == "buy" else mt5.ORDER_TYPE_SELL
        req = {"action":mt5.TRADE_ACTION_DEAL,"symbol":sym,"volume":lot,"type":ot,
               "price":price,"sl":sl,"tp":tp,"deviation":20,"magic":20260908,
               "comment":"GoldAnalyzer","type_time":mt5.ORDER_TIME_GTC,
               "type_filling":mt5.ORDER_FILLING_IOC}
        return mt5.order_send(req)

    def backtest(self, sym="XAUUSDc", tf="H1"):
        r = self.rates(sym, tf, 200)
        if r is None or len(r) < 50: return None
        c = r["close"]
        ma5 = [np.mean(c[max(0,i-4):i+1]) for i in range(len(c))]
        ma20 = [np.mean(c[max(0,i-19):i+1]) if i >= 19 else None for i in range(len(c))]
        initial = 10000; capital = initial; trades = 0; wins = 0; pos_vol = 0
        for i in range(40, len(c)):
            if ma5[i] and ma20[i] and ma5[i-1] and ma5[i-1]:
                if ma5[i-1] <= ma20[i-1] and ma5[i] > ma20[i] and pos_vol == 0:
                    if capital >= c[i] * 0.01:
                        pos_vol = (capital / c[i]) * 0.01
                        trades += 1
                elif ma5[i-1] >= ma20[i-1] and ma5[i] < ma20[i] and pos_vol > 0:
                    pnl = (c[i] - c[max(0,i-20)]) * pos_vol
                    capital += pnl
                    if pnl > 0: wins += 1
                    pos_vol = 0
        final = capital + (pos_vol * c[-1] if pos_vol > 0 else 0)
        ret = final - initial
        return {"initial_capital": initial, "final_capital": final,
                "total_return": ret/initial*100, "total_trades": trades,
                "win_rate": (wins/trades*100) if trades > 0 else 0,
                "profit_factor": abs(final/initial) if initial > 0 else 0}


class AlertSystem:
    def __init__(self):
        self.alerts = []
        self.last_alert_time = {}
        self.cooldown = 120
    def add(self, sym, threshold_pct=1.0):
        self.alerts.append({"sym": sym, "threshold": threshold_pct, "triggered": False})
        return len(self.alerts) - 1
    def remove(self, idx):
        if 0 <= idx < len(self.alerts): self.alerts.pop(idx)
    def check(self, sym, engine=None):
        import time as _tt
        now = _tt.time()
        if sym in self.last_alert_time and now - self.last_alert_time[sym] < self.cooldown: return None
        if engine:
            tick = engine.tick(sym)
        else:
            return None
        if not tick: return None
        prev = None
        for x in self.alerts:
            if x["sym"] == sym and "prev_price" in x: prev = x["prev_price"]; break
        if prev is None:
            found = False
            for x in self.alerts:
                if x["sym"] == sym: x["prev_price"] = tick.bid; found = True; break
            if not found:
                self.alerts.append({"sym": sym, "threshold": 1.0, "prev_price": tick.bid})
            return None
        chg = abs(tick.bid - prev) / prev * 100
        if chg >= 1.0:
            self.last_alert_time[sym] = now
            for x in self.alerts:
                if x["sym"] == sym: x["prev_price"] = tick.bid; break
            return {"sym": sym, "price": tick.bid, "chg": chg, "dir": "up" if tick.bid > prev else "down"}
        for x in self.alerts:
            if x["sym"] == sym: x["prev_price"] = tick.bid; break
        return None

class GoldAnalyzerApp:
    C = {'bg':'#1a1a2e','card':'#16213e','bd':'#0f3460','tx':'#e8e8e8',
         'dim':'#8892b0','acc':'#e94560','green':'#00ff88','red':'#ff4757',
         'yellow':'#ffd32a','blue':'#4fc3f7'}

    def __init__(self, root):
        self.root = root
        self.root.title("Gold Analyzer v2.0")
        self.root.geometry("1280x840")
        self.root.configure(bg=self.C['bg'])
        sw,sh = root.winfo_screenwidth(),root.winfo_screenheight()
        root.geometry(f"1280x840+{(sw-1280)//2}+{(sh-840)//2}")
        self.anz = MT5Engine()
        self.stop = False
        self._ui()
        self._refresh()
        self.root.after(3000, self._tick)
        self.root.protocol("WM_DELETE_WINDOW", self._close)

    def _ui(self):
        # Header
        hf = tk.Frame(self.root, bg=self.C['bg'])
        hf.pack(fill='x', padx=12, pady=(10,4))
        tk.Label(hf, text="\U0001f4b0 Gold Analyzer v2.0", font=('Consolas',13,'bold'),
                 fg=self.C['acc'], bg=self.C['bg']).pack(side='left')
        self.st = tk.StringVar(value="\u25cf Connecting...")
        tk.Label(hf, textvariable=self.st, font=('Consolas',10),
                 fg=self.C['dim'], bg=self.C['bg']).pack(side='right')
        self.trg = tk.StringVar(value="Target $2000 | --")
        tk.Label(hf, textvariable=self.trg, font=('Consolas',10),
                 fg=self.C['yellow'], bg=self.C['bg']).pack(side='right', padx=(20,0))

        main = tk.Frame(self.root, bg=self.C['bg'])
        main.pack(fill='both', expand=True, padx=12, pady=4)

        # Left panel
        lp = tk.Frame(main, bg=self.C['bg'])
        lp.pack(side='left', fill='both', expand=True, padx=(0,6))
        self._panel_prices(lp)
        self._panel_signal(lp)
        self._panel_account(lp)

        # Right panel
        rp = tk.Frame(main, bg=self.C['bg'])
        rp.pack(side='left', fill='both', expand=True, padx=(6,0))
        self._panel_chart(rp)
        self._panel_indicators(rp)

    def _mkframe(self, parent, title):
        f = tk.LabelFrame(parent, text=title, font=('Consolas',10,'bold'),
                          fg=self.C['tx'], bg=self.C['card'], labelanchor='n', padx=8, pady=6)
        f.pack(fill='x', pady=(0,4))
        return f

    def _panel_prices(self, parent):
        f = self._mkframe(parent, "Live Prices")
        self.pvars = {}
        for sym, name in MT5Engine.SYMBOLS.items():
            row = tk.Frame(f, bg=self.C['card'])
            row.pack(fill='x', pady=2)
            tk.Label(row, text=f"{name} ({sym})", font=('Consolas',9),
                     fg=self.C['tx'], bg=self.C['card']).pack(side='left')
            pv = tk.StringVar(value="--")
            cv = tk.StringVar(value="")
            self.pvars[sym] = (pv, cv)
            tk.Label(row, textvariable=pv, font=('Consolas',11,'bold'),
                     fg=self.C['blue'], bg=self.C['card']).pack(side='right')
            cl = tk.Label(row, textvariable=cv, font=('Consolas',8), bg=self.C['card'])
            cl.pack(side='right', padx=(4,0))
            if not hasattr(self,'pcl'): self.pcl={}
            self.pcl[sym]=cl

    def _panel_signal(self, parent):
        f = self._mkframe(parent, "Analysis Signal")
        self.sl = tk.Label(f, text="Loading...", font=('Consolas',13,'bold'),
                           fg=self.C['yellow'], bg=self.C['card'], anchor='w')
        self.sl.pack(fill='x', pady=(0,6))
        self.sd = tk.Text(f, height=6, font=('Consolas',9), fg=self.C['tx'],
                          bg=self.C['card'], wrap='word', state='disabled', relief='flat')
        self.sd.pack(fill='both', expand=True)
        bf = tk.Frame(f, bg=self.C['card'])
        bf.pack(fill='x', pady=4)
        tk.Label(bf, text="XAUUSDc Quick:", font=('Consolas',8),
                 fg=self.C['dim'], bg=self.C['card']).pack(side='left')
        for act,lot,col,txt in [('buy',0.1,self.C['green'],"+0.1"),
                                  ('sell',0.1,self.C['red'],"-0.1"),
                                  ('buy',0.5,self.C['green'],"+0.5"),
                                  ('sell',0.5,self.C['red'],"-0.5")]:
            tk.Button(bf, text=txt, command=lambda a=act,l=lot:self._trade(a,l),
                      bg=col, fg='#000' if act=='buy' else '#fff',
                      font=('Consolas',9,'bold'), cursor='hand2', relief='flat', width=6
                      ).pack(side='left', padx=2)
        # Positions
        pf = tk.LabelFrame(f, text="Positions", font=('Consolas',9,'bold'),
                           fg=self.C['tx'], bg=self.C['card'], labelanchor='n', padx=6, pady=4)
        pf.pack(fill='x', pady=(4,0))
        self.pt = tk.Text(pf, height=3, font=('Consolas',9), fg=self.C['tx'],
                          bg=self.C['card'], wrap='word', state='disabled', relief='flat')
        self.pt.pack(fill='both')

    def _panel_account(self, parent):
        f = self._mkframe(parent, "Account")
        self.avars = {}
        for k,label in [('bal','Balance'),('eq','Equity'),('mg','Margin'),
                         ('free','Free'),('prof','Profit')]:
            row = tk.Frame(f, bg=self.C['card'])
            row.pack(fill='x', pady=2)
            tk.Label(row, text=label, font=('Consolas',9), fg=self.C['dim'], bg=self.C['card']).pack(side='left')
            v = tk.StringVar(value="--")
            self.avars[k] = v
            lbl = tk.Label(row, textvariable=v, font=('Consolas',10,'bold'),
                           fg=self.C['yellow'], bg=self.C['card'])
            lbl.pack(side='right')
            if k=='prof': self.plbl=lbl

    def _panel_chart(self, parent):
        f = self._mkframe(parent, "K-Line Chart")
        tf = tk.Frame(f, bg=self.C['card'])
        tf.pack(fill='x', padx=4, pady=(0,4))
        tk.Label(tf, text="TF:", font=('Consolas',8), fg=self.C['dim'], bg=self.C['card']).pack(side='left')
        self.tv = tk.StringVar(value='H1')
        for t in ['M5','M15','H1','H4','D1']:
            tk.Radiobutton(tf, text=t, variable=self.tv, value=t,
                          bg=self.C['card'], fg=self.C['tx'], selectcolor=self.C['bd'],
                          command=self._refresh).pack(side='left', padx=4)
        self.fig = Figure(figsize=(6,4), dpi=100, facecolor=self.C['card'])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(self.C['card'])
        self.canvas = FigureCanvasTkAgg(self.fig, master=f)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        tb = NavigationToolbar2Tk(self.canvas, f)
        
        tb.update()
        tb.pack(fill='x')

    def _panel_indicators(self, parent):
        f = self._mkframe(parent, "Indicators")
        self.ivars = {}
        items = [('ma5','MA5','white'),('ma10','MA10','orange'),('ma20','MA20','blue'),
                 ('ma50','MA50','purple'),('rsi','RSI','cyan'),('macd','MACD','magenta'),
                 ('bbu','BB Up','yellow'),('bbl','BB Low','yellow'),('atr','ATR','green')]
        for i,(k,l,cl) in enumerate(items):
            if i%3==0:
                row = tk.Frame(f, bg=self.C['card'])
                row.pack(fill='x')
            dot = tk.Frame(row, width=9, height=9, bg=cl)
            dot.pack(side='left', padx=(0,4))
            tk.Label(row, text=l, font=('Consolas',8), fg=self.C['tx'], bg=self.C['card']).pack(side='left')
            v = tk.StringVar(value="--")
            self.ivars[k] = v
            tk.Label(row, textvariable=v, font=('Consolas',8,'bold'), fg=cl, bg=self.C['card']).pack(side='right', padx=(12,0))
        vf = tk.Frame(f, bg=self.C['card'])
        vf.pack(fill='x', pady=4)
        tk.Label(vf, text="Volatility(ATR):", font=('Consolas',8), fg=self.C['dim'], bg=self.C['card']).pack(side='left')
        self.vv = tk.StringVar(value="--")
        tk.Label(vf, textvariable=self.vv, font=('Consolas',8,'bold'), fg=self.C['tx'], bg=self.C['card']).pack(side='right')

    def _trade(self, act, lot):
        r = self.anz.order('XAUUSDc', act, lot)
        if r and r.retcode == mt5.TRADE_RETCODE_DONE:
            messagebox.showinfo("OK", f"{act.upper()} {lot} XAUUSDc\nOrder: {r.order}")
            self._refresh()
        else:
            e = r.comment if r else "Failed"
            messagebox.showerror("Fail", f"{e}\nCode: {r.retcode if r else 'N/A'}")

    def _refresh(self):
        try:
            if not self.anz.ok:
                if self.anz.__init__():
                    self.st.set("\u25cf Connected")
                    self.st.config(fg=self.C['green'])
                else:
                    self.st.set("\u25cf Disconnected"); self.st.config(fg=self.C['red']); return
            self._prices(); self._account(); self._signal(); self._chart(); self._target()
        except Exception as e:
            print(f"Err: {e}")

    def _tick(self):
        if not self.stop:
            self._refresh()
            self.root.after(3000, self._tick)

    def _prices(self):
        for sym in MT5Engine.SYMBOLS:
            t = self.anz.tick(sym)
            if t:
                pv,cv = self.pvars[sym]
                dig = 2 if sym=='XAUUSDc' else (3 if sym=='USDJPYc' else 5)
                pv.set(f"{t.bid:.{dig}f}")
                r = self.anz.rates(sym,'H1',10)
                if r and len(r)>1:
                    ch = t.bid - r[-1]['close']
                    pct = ch/r[-1]['close']*100
                    sg = "+" if ch>=0 else ""
                    co = self.C['green'] if ch>=0 else self.C['red']
                    cv.set(f"{sg}{ch:.{dig}f} ({sg}{pct:.2f}%)")
                    self.pcl[sym].config(fg=co)

    def _account(self):
        i = self.anz.account()
        if i:
            for k in ['bal','eq','mg','free']: self.avars[k].set(f"${i[k]:,.2f}")
            p = i['profit']
            self.avars['prof'].set(f"${p:+,.2f}")
            self.plbl.config(fg=self.C['green'] if p>=0 else self.C['red'])
            ps = self.anz.positions('XAUUSDc')
            txt = ""
            if ps:
                tick = self.anz.tick('XAUUSDc')
                for p in ps:
                    d = "SELL" if p.type==mt5.POSITION_TYPE_SELL else "BUY"
                    pnl = (p.price_open-tick.bid)*p.volume*100 if p.type==mt5.POSITION_TYPE_SELL else (tick.bid-p.price_open)*p.volume*100
                    st = "P" if pnl>=0 else "L"
                    co = self.C['green'] if pnl>=0 else self.C['red']
                    txt += f"{d} {p.volume}@{p.price_open:.2f} {st}${abs(pnl):.0f}\n"
            else:
                txt = "No position"
            self.pt.config(state='normal'); self.pt.delete('1.0','end'); self.pt.insert('1.0',txt); self.pt.config(state='disabled')

    def _signal(self):
        a = self.anz.analyze('XAUUSDc', self.tv.get())
        if not a: return
        txt, col = a['overall']
        cm = {'green':self.C['green'],'red':self.C['red'],'orange':self.C['yellow'],
              'lightgreen':self.C['green'],'gray':self.C['dim']}
        self.sl.config(text=txt, fg=cm.get(col,self.C['yellow']))
        d = f"Trend: {a['trend']}\nScore: Buy {a['bs']} | Sell {a['ss']}\n"
        if a['sup']: d += f"Support: ${a['sup']:.1f}  Resistance: ${a['res']:.1f}\n"
        d += "\n"
        for n,l in a['signals']:
            lc = self.C['green'] if l in ('Buy','Bullish','Strong') else (
                self.C['red'] if l in ('Sell','Bearish','Strong') else self.C['yellow'])
            d += f"* {n}: {l}\n"
        self.sd.config(state='normal'); self.sd.delete('1.0','end'); self.sd.insert('1.0',d); self.sd.config(state='disabled')
        self.ivars['ma5'].set(f"{a['ma'].get(5,0):.2f}")
        self.ivars['ma10'].set(f"{a['ma'].get(10,0):.2f}")
        self.ivars['ma20'].set(f"{a['ma'].get(20,0):.2f}")
        self.ivars['ma50'].set(f"{a['ma'].get(50,0):.2f}")
        self.ivars['rsi'].set(f"{a['rsi']:.1f}")
        self.ivars['macd'].set(f"{a['macd']:.2f}")
        if a['bb']:
            self.ivars['bbu'].set(f"{a['bb'][0]:.2f}")
            self.ivars['bbl'].set(f"{a['bb'][2]:.2f}")
        self.ivars['atr'].set(f"{a['atr']:.2f}")
        self.vv.set(f"{a['atr_pct']:.2f}% ({a['vol']})")

    def _chart(self):
        self.fig.clear()
        a = self.anz.analyze('XAUUSDc', self.tv.get())
        if not a: return
        r = a['rates']; n = min(len(r),60)
        ti = np.arange(n)
        cl = r[-n:]['close']; op = r[-n:]['open']
        hi = r[-n:]['high']; lo = r[-n:]['low']
        m5 = np.convolve(cl, np.ones(5)/5, mode='valid')
        m10 = np.convolve(cl, np.ones(10)/10, mode='valid')
        m20 = np.convolve(cl, np.ones(20)/20, mode='valid')
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(self.C['card'])
        for i in range(n):
            co = self.C['green'] if cl[i]>=op[i] else self.C['red']
            ax.plot([ti[i],ti[i]],[lo[i],hi[i]],color=co,lw=0.7)
            ax.add_patch(Rectangle((ti[i]-0.3,min(cl[i],op[i])),0.6,abs(cl[i]-op[i]),
                                    facecolor=co,edgecolor=co))
        o=n-len(m5); ax.plot(ti[o:],m5,'white',lw=1,label='MA5')
        o=n-len(m10); ax.plot(ti[o:],m10,'orange',lw=1,label='MA10')
        o=n-len(m20); ax.plot(ti[o:],m20,'blue',lw=1,label='MA20')
        if a['sup']: ax.axhline(y=a['sup'],color='green',ls='--',alpha=0.5,label='Support')
        if a['res']: ax.axhline(y=a['res'],color='red',ls='--',alpha=0.5,label='Resistance')
        ax.set_title(f"XAUUSDc {self.tv.get()}  Price: {a['price']:.2f}", color=self.C['tx'], fontsize=10)
        ax.tick_params(colors=self.C['dim'])
        for sp in ax.spines.values(): sp.set_color(self.C['bd'])
        ax.legend(loc='upper left', facecolor=self.C['card'], edgecolor=self.C['bd'], labelcolor=self.C['tx'])
        self.fig.tight_layout(); self.canvas.draw()

    def _target(self):
        i = self.anz.account()
        if i:
            rem = 2000 - i['balance']
            self.trg.set(f"Target $2000 | Current ${i['balance']:.0f} | {'DONE' if i['balance']>=2000 else f'Need +${rem:.0f}'}")

    def _close(self):
        self.stop = True
        self.anz.shutdown()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = GoldAnalyzerApp(root)
    root.mainloop()
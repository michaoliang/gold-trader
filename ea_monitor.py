# -*- coding: utf-8 -*-
import MetaTrader5 as mt5
import time
import json
import os
from datetime import datetime, date

LOG_FILE = r'E:\MySoftware\黄金分析工具_Portable\ea_monitor_log.txt'
STATE_FILE = r'E:\MySoftware\黄金分析工具_Portable\ea_monitor_state.json'

def log(msg, level="INFO"):
    ts = datetime.now().strftime("%H:%M:%S")
    line = "[%s] [%s] %s" % (ts, level, msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")
        f.flush()
    print(line, flush=True)

def get_account():
    try:
        acc = mt5.account_info()
        if acc is None: return None
        return {"balance": float(acc.balance), "equity": float(acc.equity)}
    except: return None

def get_positions():
    try:
        pos = mt5.positions_get(symbol="XAUUSDc")
        return list(pos) if pos else []
    except: return []

def run():
    if not mt5.initialize():
        log("MT5 init failed", "ERROR")
        return
    log("=" * 40)
    log("EA监控启动 - 只监控不交易")
    log("=" * 40)
    while True:
        try:
            acc = get_account()
            if acc is None:
                log("等待MT5...", "WARN")
                time.sleep(15)
                continue
            positions = get_positions()
            pnl = 0
            if positions:
                tick = mt5.symbol_info_tick("XAUUSDc")
                for p in positions:
                    is_buy = p.type == mt5.POSITION_TYPE_BUY
                    pnl = (float(tick.bid)-float(p.price_open))*float(p.volume)*100 if is_buy else (float(p.price_open)-float(tick.bid))*float(p.volume)*100
            progress = (acc["balance"] - 1560) / (3000 - 1560) * 100
            log("余额=$%.2f 净值=$%.2f 浮动盈亏=$%.2f 进度=%.1f%%" % (acc["balance"], acc["equity"], pnl, progress))
            if positions:
                for p in positions:
                    d = "BUY" if p.type == mt5.POSITION_TYPE_BUY else "SELL"
                    log("  持仓: %s %.2f手 @ %.3f" % (d, p.volume, p.price_open))
            else:
                log("  无持仓")
            time.sleep(10)
        except Exception as e:
            log("错误: %s" % e, "ERROR")
            time.sleep(15)
    mt5.shutdown()

if __name__ == "__main__":
    run()

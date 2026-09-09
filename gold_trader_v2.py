# -*- coding: utf-8 -*-
import MetaTrader5 as mt5
import time
import json
import os
from datetime import datetime, date

CFG = {
    'auto_trade': False,  # True=自动交易, False=只监控分析
    'target_balance': 3000.0,
    'initial_balance': 1560.0,
    'symbol': 'XAUUSDc',
    'lot_base': 0.05,
    'lot_max': 0.20,
    'risk_per_trade_pct': 2.0,
    'reward_per_trade_pct': 4.0,
    'max_positions': 3,
    'cooldown_sec': 180,
    'log_file': r'E:/MySoftware/黄金分析工具_Portable/trader_v2_log.txt',
    'state_file': r'E:/MySoftware/黄金分析工具_Portable/trader_v2_state.json',
}

def log(msg, level='INFO'):
    ts = datetime.now().strftime('%H:%M:%S')
    line = '[%s] [%s] %s' % (ts, level.rjust(6), msg)
    with open(CFG['log_file'], 'a', encoding='utf-8') as f:
        f.write(line + chr(10))
        f.flush()
    print(line, flush=True)

def save_state(state):
    with open(CFG['state_file'], 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

def load_state():
    if os.path.exists(CFG['state_file']):
        with open(CFG['state_file'], 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'last_trade_time': 0, 'consecutive_losses': 0, 'daily_pnl': 0.0, 'trade_count': 0}

def calc_rsi(prices, period=14):
    if len(prices) < period + 1:
        return 50.0
    gains, losses = [], []
    for i in range(1, len(prices)):
        d = prices[i] - prices[i-1]
        gains.append(d if d > 0 else 0)
        losses.append(abs(d) if d < 0 else 0)
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    if avg_loss == 0:
        return 100.0
    return 100.0 - (100.0 / (1.0 + avg_gain / avg_loss))

def calc_ema(data, period):
    if len(data) < period:
        return sum(data) / max(len(data), 1)
    k = 2.0 / (period + 1)
    ema = data[0]
    for price in data[1:]:
        ema = price * k + ema * (1 - k)
    return ema

def analyze_market(symbol):
    try:
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return None
        rates_h1 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 50)
        rates_m15 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 50)
        rates_m5 = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 30)
        if rates_h1 is None or len(rates_h1) < 30:
            return None
        closes_h1 = [float(r['close']) for r in rates_h1]
        closes_m15 = [float(r['close']) for r in rates_m15] if (rates_m15 is not None and len(rates_m15) > 0) else closes_h1
        closes_m5 = [float(r['close']) for r in rates_m5] if (rates_m5 is not None and len(rates_m5) > 0) else closes_h1
        price = float(tick.bid)
        ask = float(tick.ask)
        rsi_h1 = calc_rsi(closes_h1, 14)
        rsi_m15 = calc_rsi(closes_m15, 14)
        rsi_m5 = calc_rsi(closes_m5, 14)
        ema5 = calc_ema(closes_h1, 5)
        ema20 = calc_ema(closes_h1, 20)
        ema50 = calc_ema(closes_h1, 50)
        if ema5 > ema20 > ema50:
            trend, ts_val = 'UP', 3
        elif ema5 < ema20 < ema50:
            trend, ts_val = 'DOWN', -3
        elif ema5 > ema20:
            trend, ts_val = 'WEAK_UP', 1
        elif ema5 < ema20:
            trend, ts_val = 'WEAK_DOWN', -1
        else:
            trend, ts_val = 'SIDE', 0
        score = 0
        if rsi_h1 < 30: score += 4
        elif rsi_h1 < 40: score += 2
        elif rsi_h1 > 70: score -= 4
        elif rsi_h1 > 60: score -= 2
        if rsi_m15 < 35: score += 2
        elif rsi_m15 > 65: score -= 2
        score += ts_val
        if price < ema20 * 0.995: score += 1
        elif price > ema20 * 1.005: score -= 1
        if len(closes_m5) >= 5:
            m5_ma = sum(closes_m5[-5:]) / 5
            if rsi_h1 < 40 and m5_ma > closes_m5[-1]: score += 1
            elif rsi_h1 > 60 and m5_ma < closes_m5[-1]: score -= 1
        return {'price': price, 'ask': ask, 'rsi_h1': rsi_h1, 'rsi_m15': rsi_m15, 'rsi_m5': rsi_m5, 'trend': trend, 'score': score, 'ema5': ema5, 'ema20': ema20, 'ema50': ema50}
    except Exception as e:
        log('Analysis error: %s' % e, 'ERROR')
        return None

def get_account():
    try:
        acc = mt5.account_info()
        if acc is None: return None
        return {'balance': float(acc.balance), 'equity': float(acc.equity), 'margin': float(acc.margin), 'free_margin': float(acc.margin_free), 'profit': float(acc.profit)}
    except: return None

def get_positions(symbol):
    try:
        pos = mt5.positions_get(symbol=symbol)
        return list(pos) if pos else []
    except: return []

def calc_pnl(positions):
    try:
        tick = mt5.symbol_info_tick(CFG['symbol'])
        if tick is None: return 0.0
        total = 0.0
        for p in positions:
            is_buy = p.type == mt5.POSITION_TYPE_BUY
            pnl = (float(tick.bid)-float(p.price_open))*float(p.volume)*100 if is_buy else (float(p.price_open)-float(tick.bid))*float(p.volume)*100
            total += pnl
        return total
    except: return 0.0

def open_trade(direction, lot, symbol):
    try:
        tick = mt5.symbol_info_tick(symbol)
        if tick is None: return False, 'No quote'
        price = float(tick.ask) if direction == 'BUY' else float(tick.bid)
        sl_pct = CFG['risk_per_trade_pct'] / 100.0
        tp_pct = CFG['reward_per_trade_pct'] / 100.0
        if direction == 'BUY':
            sl = price * (1 - sl_pct)
            tp = price * (1 + tp_pct)
        else:
            sl = price * (1 + sl_pct)
            tp = price * (1 - tp_pct)
        order_type = mt5.ORDER_TYPE_BUY if direction == 'BUY' else mt5.ORDER_TYPE_SELL
        req = {'action': mt5.TRADE_ACTION_DEAL, 'symbol': symbol, 'volume': lot, 'type': order_type, 'price': price, 'sl': sl, 'tp': tp, 'deviation': 30, 'magic': 20260909, 'comment': 'GoldTrader_v2', 'type_time': mt5.ORDER_TIME_GTC, 'type_filling': mt5.ORDER_FILLING_FOK}
        res = mt5.order_send(req)
        if res is None: return False, 'None response'
        if res.retcode != mt5.TRADE_RETCODE_DONE: return False, 'err:%d %s' % (res.retcode, res.comment)
        return True, 'ok %s %.2f' % (direction, price)
    except Exception as e:
        return False, 'exc: %s' % e

def run():
    if not mt5.initialize():
        log('MT5 init failed: %s' % mt5.last_error(), 'ERROR')
        return
    log('=' * 50)
    log('Gold Trader v2.0 STARTED')
    log('Target: %.0f | Initial: %.0f' % (CFG['target_balance'], CFG['initial_balance']))
    log('Risk: %.1f%% | Reward: %.1f%% | MaxPos: %d | Cooldown: %ds' % (CFG['risk_per_trade_pct'], CFG['reward_per_trade_pct'], CFG['max_positions'], CFG['cooldown_sec']))
    log('=' * 50)
    state = load_state()
    last_trade_time = state.get('last_trade_time', 0)
    consecutive_losses = state.get('consecutive_losses', 0)
    daily_pnl = state.get('daily_pnl', 0.0)
    trade_count = state.get('trade_count', 0)
    balance = CFG['initial_balance']
    while True:
        try:
            acc = get_account()
            if acc is None:
                log('No account info, waiting...', 'WARN')
                time.sleep(15)
                continue
            balance = acc['balance']
            equity = acc['equity']
            profit = acc['profit']
            progress = (balance - CFG['initial_balance']) / (CFG['target_balance'] - CFG['initial_balance']) * 100
            log('Bal=%.2f Eq=%.2f PnL=%.2f Prog=%.1f%%' % (balance, equity, profit, progress))
            if balance >= CFG['target_balance']:
                log('*** TARGET REACHED $%.2f ***' % balance, 'SUCCESS')
                break
            if balance <= CFG['initial_balance'] * 0.85:
                log('*** CAPITAL PROTECTION %.2f ***' % balance, 'WARNING')
                break
            positions = get_positions(CFG['symbol'])
            total_pnl = calc_pnl(positions)
            if positions:
                for p in positions:
                    is_buy = p.type == mt5.POSITION_TYPE_BUY
                    tk = mt5.symbol_info_tick(CFG['symbol'])
                    if tk:
                        pnl_v = (float(tk.bid)-float(p.price_open))*float(p.volume)*100 if is_buy else (float(p.price_open)-float(tk.bid))*float(p.volume)*100
                        d_str = 'BUY' if is_buy else 'SELL'
                        log('  Pos: %s %.2f @ %.3f PnL=$%.2f' % (d_str, p.volume, p.price_open, pnl_v))
            else:
                log('  No positions')
            for p in list(positions):
                is_buy = p.type == mt5.POSITION_TYPE_BUY
                tk = mt5.symbol_info_tick(CFG['symbol'])
                if tk is None: continue
                po = float(p.price_open)
                vol = float(p.volume)
                cpnl = (float(tk.bid) - po) * vol * 100 if is_buy else (po - float(tk.bid)) * vol * 100
                if cpnl >= 50:
                    log('  TP +$%.1f close #%d' % (cpnl, p.ticket), 'SUCCESS')
                    req = {'action': mt5.TRADE_ACTION_DEAL, 'symbol': CFG['symbol'], 'volume': vol, 'type': mt5.ORDER_TYPE_SELL if is_buy else mt5.ORDER_TYPE_BUY, 'position': int(p.ticket), 'price': float(tk.ask) if is_buy else float(tk.bid), 'deviation': 30, 'magic': 20260909, 'type_time': mt5.ORDER_TIME_GTC, 'type_filling': mt5.ORDER_FILLING_FOK}
                    mt5.order_send(req)
                    consecutive_losses = 0 if cpnl >= 0 else consecutive_losses + 1
                    daily_pnl += cpnl
                    trade_count += 1
                    last_trade_time = time.time()
                    time.sleep(30)
                    break
                elif cpnl <= -30:
                    log('  SL $%.1f close #%d' % (cpnl, p.ticket), 'WARNING')
                    req = {'action': mt5.TRADE_ACTION_DEAL, 'symbol': CFG['symbol'], 'volume': vol, 'type': mt5.ORDER_TYPE_SELL if is_buy else mt5.ORDER_TYPE_BUY, 'position': int(p.ticket), 'price': float(tk.ask) if is_buy else float(tk.bid), 'deviation': 30, 'magic': 20260909, 'type_time': mt5.ORDER_TIME_GTC, 'type_filling': mt5.ORDER_FILLING_FOK}
                    mt5.order_send(req)
                    consecutive_losses += 1
                    daily_pnl += cpnl
                    trade_count += 1
                    last_trade_time = time.time()
                    time.sleep(30)
                    break
            positions = get_positions(CFG['symbol'])
            if consecutive_losses >= 2:
                log('Consecutive losses %d, pause 10min' % consecutive_losses, 'WARNING')
                time.sleep(600)
                continue
            if daily_pnl <= -50:
                log('Daily loss $%.1f, pause 30min' % daily_pnl, 'WARNING')
                time.sleep(1800)
                daily_pnl = 0.0
                continue
            if len(positions) < CFG['max_positions']:
                now = time.time()
                if (now - last_trade_time) > CFG['cooldown_sec'] and CFG['auto_trade']:
                    market = analyze_market(CFG['symbol'])
                    if market:
                        sc = market['score']
                        log('  Analysis: RSI_H1=%.1f RSI_M15=%.1f Trend=%s Score=%+d Price=%.2f' % (market['rsi_h1'], market['rsi_m15'], market['trend'], sc, market['price']))
                        if sc >= 4:
                            lot = min(CFG['lot_max'], round(CFG['lot_base'] * (1 + abs(sc) * 0.1), 2))
                            ok, msg = open_trade('BUY', lot, CFG['symbol'])
                            if ok:
                                log('  >>> BUY %.2f @ %.2f' % (lot, market['price']), 'TRADE')
                                last_trade_time = now
                                consecutive_losses = 0
                            else:
                                log('  BUY failed: %s' % msg, 'ERROR')
                        elif sc <= -4:
                            lot = min(CFG['lot_max'], round(CFG['lot_base'] * (1 + abs(sc) * 0.1), 2))
                            ok, msg = open_trade('SELL', lot, CFG['symbol'])
                            if ok:
                                log('  >>> SELL %.2f @ %.2f' % (lot, market['price']), 'TRADE')
                                last_trade_time = now
                                consecutive_losses = 0
                            else:
                                log('  SELL failed: %s' % msg, 'ERROR')
                    time.sleep(15)
                else:
                    rem = int(CFG['cooldown_sec'] - (now - last_trade_time))
                    if int(time.time()) % 30 == 0:
                        log('  Cooldown %ds remaining' % rem)
            else:
                log('Max positions %d reached' % CFG['max_positions'])
            if int(time.time()) % 60 < 2:
                save_state({'last_trade_time': last_trade_time, 'consecutive_losses': consecutive_losses, 'daily_pnl': daily_pnl, 'trade_count': trade_count})
            time.sleep(10)
        except Exception as e:
            log('Main loop error: %s' % e, 'ERROR')
            time.sleep(15)
    mt5.shutdown()
    log('DONE | Trades: %d | Final: $%.2f' % (trade_count, balance), 'INFO')

if __name__ == '__main__':
    run()

while ($true) {
    $log = Get-Content "E:\MySoftware\黄金分析工具_Portable\trade_log.txt" -ErrorAction SilentlyContinue | Select-Object -Last 1
    Write-Host $log
    
    python -c "
import MetaTrader5 as mt5
ok = mt5.initialize()
if ok:
    acc = mt5.account_info()
    pos = mt5.positions_get(symbol='XAUUSDc')
    tick = mt5.symbol_info_tick('XAUUSDc')
    pnl = 0
    if pos:
        for p in pos:
            is_buy = p.type == mt5.POSITION_TYPE_BUY
            pnl = (float(tick.bid) - float(p.price_open)) * float(p.volume) * 100 if is_buy else (float(p.price_open) - float(tick.bid)) * float(p.volume) * 100
    progress = (float(acc.balance) - 1560) / (3000 - 1560) * 100
    print(f'Balance: {float(acc.balance):.2f} Positions: {len(pos) if pos else 0} PnL: {pnl:+.2f} Progress: {progress:.1f}%')
    mt5.shutdown()
"
    
    Start-Sleep -Seconds 60
}

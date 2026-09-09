$script = {
    python -c "
import MetaTrader5 as mt5
ok = mt5.initialize()
if ok:
    tick = mt5.symbol_info_tick('XAUUSDc')
    pos = mt5.positions_get(symbol='XAUUSDc')
    acc = mt5.account_info()
    
    total_pnl = 0
    if pos is not None and len(pos) > 0:
        for p in pos:
            is_buy = p.type == mt5.POSITION_TYPE_BUY
            pnl = (float(tick.bid) - float(p.price_open)) * float(p.volume) * 100 if is_buy else (float(p.price_open) - float(tick.bid)) * float(p.volume) * 100
            total_pnl += pnl
    
    rates = mt5.copy_rates_from_pos('XAUUSDc', mt5.TIMEFRAME_H1, 0, 20)
    high_20 = max([float(r['high']) for r in rates[-20:]]) if rates is not None else 0
    low_20 = min([float(r['low']) for r in rates[-20:]]) if rates is not None else 0
    
    progress = (float(acc.balance) - 1560) / (3000 - 1560) * 100
    
    print('Price:', round(float(tick.bid), 2), '| High20:', round(high_20, 2), '| Low20:', round(low_20, 2))
    print('Balance:', round(float(acc.balance), 2), '| PnL:', round(total_pnl, 2), '| Progress:', round(progress, 1), '%')
    
    if float(tick.bid) >= high_20:
        print('>>> BUY SIGNAL DETECTED!')
    elif float(tick.bid) <= low_20:
        print('>>> SELL SIGNAL DETECTED!')
    else:
        print('Wait for breakout...')
    
    mt5.shutdown()
"
}

Write-Host "=== Turtle Bot Monitor ==="
Write-Host "Monitoring every 60 seconds for 1 hour..."
Write-Host ""

for ($i = 1; $i -le 60; $i++) {
    & $script
    Start-Sleep -Seconds 60
}

Write-Host ""
Write-Host "=== 1 Hour Monitor Complete ==="
Get-Content "E:\MySoftware\黄金分析工具_Portable\turtle_log.txt" -ErrorAction SilentlyContinue | Select-Object -Last 5

# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py'
with open(filepath, encoding='utf-8') as f:
    content = f.read()

# 替换信号分析方法
old = '''        d = f"Trend: {a['trend']}\nScore: Buy {a['bs']} | Sell {a['ss']}\n"
        if a["sup"]: d += f"Support: ${a['sup']:.1f}  Resistance: ${a['res']:.1f}\n"
        d += "\n"
        for n, l in a["signals"]:
            lc = self.C["green"] if l in ("买入", "偏多", "强势") else (self.C["red"] if l in ("卖出", "偏空", "强势") else self.C["yellow"])
            d += f"* {n}: {l}\n"
        self.sd.config(state="normal"); self.sd.delete("1.0", "end"); self.sd.insert("1.0", d); self.sd.config(state="disabled")'''

new = '''        # 简体中文 + 科技感样式
        trend_cn = {"上涨": "📈 上升趋势", "下跌": "📉 下降趋势", "盘整": "➡️ 横盘整理"}.get(a["trend"], a["trend"])
        d = "┌─ 趋势分析 ─────────────────┐\n"
        d += f"│ {trend_cn:<22} │\n"
        d += f"│ 多头得分: {a['bs']:>3}  |  空头得分: {a['ss']:>3}   │\n"
        d += "└────────────────────────────┘\n\n"
        if a["sup"]: d += f"[支撑位] ${a['sup']:.1f}      [阻力位] ${a['res']:.1f}\n\n"
        d += "┌─ 技术指标 ─────────────────┐\n"
        for n, l in a["signals"]:
            icon = "●" if l in ("买入", "偏多") else ("●" if l in ("卖出", "偏空") else "○")
            d += f"│ {icon} {n:<18} {l}  │\n"
        d += "└────────────────────────────┘"
        self.sd.config(state="normal"); self.sd.delete("1.0", "end"); self.sd.insert("1.0", d); self.sd.config(state="disabled")'''

if old in content:
    content = content.replace(old, new)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('信号分析已更新')
else:
    print('未找到目标文本，检查空格或编码')

# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py'
with open(filepath, encoding='utf-8') as f:
    lines = f.readlines()

# 找到并替换信号输出部分（第741-748行，索引从0开始）
new_lines = lines[:740]
new_lines.append('        # 简体中文 + 科技感样式\n')
new_lines.append('        trend_cn = {"上涨": "\U0001f4c8 上升趋势", "下跌": "\U0001f4c9 下降趋势", "盘整": "\u27a1\ufe0f 横盘整理"}.get(a["trend"], a["trend"])\n')
new_lines.append('        d = "\u250c\u2500 趋势分析 \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510\n"\n')
new_lines.append('        d += "| " + trend_cn + " " * (20 - len(trend_cn)) + " |\n"\n')
new_lines.append('        d += "| 多头得分: {:<3} |  空头得分: {:<3}   |\n".format(a["bs"], a["ss"])\n')
new_lines.append('        d += "\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518\n\n"\n')
new_lines.append('        if a["sup"]: d += "[支撑位] ${:.1f}      [阻力位] ${:.1f}\n\n".format(a["sup"], a["res"])\n')
new_lines.append('        d += "\u250c\u2500 技术指标 \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2510\n"\n')
new_lines.append('        for n, l in a["signals"]:\n')
new_lines.append('            icon = "\u25cf" if l in ("买入", "偏多") else ("\u25cf" if l in ("卖出", "偏空") else "\u25cb")\n')
new_lines.append('            d += "| {} {:<16} {}  |\n".format(icon, n, l)\n')
new_lines.append('        d += "\u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518"\n')
new_lines.append('        self.sd.config(state="normal"); self.sd.delete("1.0", "end"); self.sd.insert("1.0", d); self.sd.config(state="disabled")\n')
new_lines.extend(lines[748:])

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('信号分析已更新为简体中文+科技感样式')

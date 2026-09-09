# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py'
with open(filepath, encoding='utf-8') as f:
    content = f.read()

# 找到问题区域并开始修复
# 删除从 "# 简体中文" 到 "self.sd.config" 之间的错误代码
start_marker = '# 简体中文 + 科技感样式'
end_marker = 'self.sd.config(state="normal"); self.sd.delete("1.0", "end"); self.sd.insert("1.0", d); self.sd.config(state="disabled")'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker) + len(end_marker)

if start_idx >= 0 and end_idx >= 0:
    # 构建新的正确代码
    new_code = '''        # 简体中文 + 科技感样式
        trend_cn = {"上涨": "\\U0001f4c8 上升趋势", "下跌": "\\U0001f4c9 下降趋势", "盘整": "\\u27a1\\ufe0f 横盘整理"}.get(a["trend"], a["trend"])
        d = "\\u250c\\u2500 趋势分析 \\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2510\\n"
        d += "| " + trend_cn + " " * (20 - len(trend_cn)) + " |\\n"
        d += "| 多头得分: {:<3} |  空头得分: {:<3}   |\\n".format(a["bs"], a["ss"])
        d += "\\u2514\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2518\\n\\n"
        if a["sup"]: d += "[支撑位] ${:.1f}      [阻力位] ${:.1f}\\n\\n".format(a["sup"], a["res"])
        d += "\\u250c\\u2500 技术指标 \\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2510\\n"
        for n, l in a["signals"]:
            icon = "\\u25cf" if l in ("\\u4e70\\u5165", "\\u504f\\u591a") else ("\\u25cf" if l in ("\\u5356\\u51fa", "\\u504f\\u7a7a") else "\\u25cb")
            d += "| {} {:<16} {}  |\\n".format(icon, n, l)
        d += "\\u2514\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2500\\u2518"
        self.sd.config(state="normal"); self.sd.delete("1.0", "end"); self.sd.insert("1.0", d); self.sd.config(state="disabled")'''
    
    content = content[:start_idx] + new_code + content[end_idx:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print('语法错误已修复')
else:
    print(f'未找到标记: start={start_idx}, end={end_idx}')

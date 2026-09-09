# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py'
with open(filepath, encoding='utf-8') as f:
    content = f.read()

# 修复 \$ 问题
old_text = '[支撑位] \\${:.1f}      [阻力位] \\${:.1f}'
new_text = '[支撑位] ${:.1f}      [阻力位] ${:.1f}'
content = content.replace(old_text, new_text)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('已修复')

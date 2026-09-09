# -*- coding: utf-8 -*-
with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = 'command=lambda o=opt: self.chart_tv.set(o) or self.tv.set(o) or self._chart_m1(); self._chart_h1() or self._signal()).pack(side=\'left\', padx=4)'
new = 'command=lambda o=opt: (self.chart_tv.set(o), self.tv.set(o), self._chart_m1(), self._chart_h1(), self._signal())[-1]).pack(side=\'left\', padx=4)'

if old in content:
    content = content.replace(old, new)
    with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('已修复')
else:
    print('未找到，显示第558行')
    lines = content.split(chr(10))
    if len(lines) >= 558:
        print(repr(lines[557]))

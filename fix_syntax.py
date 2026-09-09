# -*- coding: utf-8 -*-
with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复第558行的语法错误
# 旧的代码: command=lambda o=opt: self.chart_tv.set(o) or self.tv.set(o) or self._chart_m1(); self._chart_h1() or self._signal()).pack(side='left', padx=4)
# 新的代码: 使用一个辅助函数来执行多个操作

old_pattern = '''command=lambda o=opt: self.chart_tv.set(o) or self.tv.set(o) or self._chart_m1(); self._chart_h1() or self._signal()).pack(side='left', padx=4)'''

new_pattern = '''command=lambda o=opt: (self.chart_tv.set(o), self.tv.set(o), self._chart_m1(), self._chart_h1(), self._signal())[-1]).pack(side='left', padx=4)'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('已修复')
else:
    print('未找到目标模式，显示第558行:')
    lines = content.split('\n')
    if len(lines) >= 558:
        print(f'第558行: {lines[557]}')

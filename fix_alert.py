# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py'
with open(filepath, encoding='utf-8') as f:
    lines = f.readlines()

# 找到并修改预警面板
new_lines = []
for i, line in enumerate(lines):
    # 在 __init__ 中添加阈值显示变量
    if 'self.conn_var = tk.StringVar(value="连接中...")' in line:
        new_lines.append(line)
        new_lines.append('        self.alert_thresh_var = tk.StringVar(value="1.0%")  # 实时阈值显示\n')
        continue
    
    # 修改预警面板 - 在按钮后添加阈值显示
    if 'tk.Button(af, text="添加预警"' in line:
        new_lines.append(line)
        # 在按钮后添加阈值显示标签
        indent = '        '
        new_lines.append(f'{indent}self.alert_thresh_lbl = tk.Label(af, textvariable=self.alert_thresh_var, font=("Consolas", 9, "bold"),\n')
        new_lines.append(f'{indent}                                 fg=self.C["yellow"], bg=self.C["card"])')
        new_lines.append(f'{indent}self.alert_thresh_lbl.pack(side="left", padx=(10, 0))\n')
        continue
    
    # 在 Spinbox 后添加 trace
    if 'tk.Spinbox(af, from_=0.5, to=10, increment=0.5, textvariable=self.alert_pct' in line:
        new_lines.append(line)
        # 找到这行的结束位置，在同一行或下一行添加 trace
        if 'pack(side="left"' in line:
            # 修改这行，在 pack 前添加 trace
            new_lines[-1] = line.replace(').pack(side="left", padx=(0,8))', 
                ').pack(side="left", padx=(0,8))\n        self.alert_pct.trace_add("write", lambda *args: self.alert_thresh_var.set(f"{self.alert_pct.get():.1f}%"))\n')
        continue
    
    new_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('阈值显示已添加')

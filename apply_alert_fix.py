# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py'
with open(filepath, encoding='utf-8') as f:
    content = f.read()

# 1. 在 __init__ 中添加阈值显示变量
old = '        self.conn_var = tk.StringVar(value="连接中...")'
new = '        self.conn_var = tk.StringVar(value="连接中...")\n        self.alert_thresh_var = tk.StringVar(value="1.0%")  # 实时阈值显示'
content = content.replace(old, new)

# 2. 修改预警面板，添加阈值显示和 trace
old_alert = '''        tk.Button(af, text="添加预警", command=self._add_alert,
                  bg=self.C["accent"], fg=self.C["bg"], font=("Consolas", 9), cursor="hand2", relief="flat", width=8).pack(side="left")'''
new_alert = '''        tk.Button(af, text="添加预警", command=self._add_alert,
                  bg=self.C["accent"], fg=self.C["bg"], font=("Consolas", 9), cursor="hand2", relief="flat", width=8).pack(side="left")
        # 实时阈值显示
        self.alert_thresh_lbl = tk.Label(af, textvariable=self.alert_thresh_var, font=("Consolas", 9, "bold"),
                                         fg=self.C["yellow"], bg=self.C["card"])
        self.alert_thresh_lbl.pack(side="left", padx=(10, 0))'''
content = content.replace(old_alert, new_alert)

# 3. 在 Spinbox 后添加 trace
old_spinbox = '''        tk.Spinbox(af, from_=0.5, to=10, increment=0.5, textvariable=self.alert_pct, width=5,
                   font=("Consolas", 9), bg=self.C["bg"], fg=self.C["tx"], relief="flat").pack(side="left", padx=(0,8))'''
new_spinbox = '''        tk.Spinbox(af, from_=0.5, to=10, increment=0.5, textvariable=self.alert_pct, width=5,
                   font=("Consolas", 9), bg=self.C["bg"], fg=self.C["tx"], relief="flat").pack(side="left", padx=(0,8))
        self.alert_pct.trace_add("write", lambda *args: self.alert_thresh_var.set("{:.1f}%".format(self.alert_pct.get())))'''
content = content.replace(old_spinbox, new_spinbox)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('阈值显示已添加')

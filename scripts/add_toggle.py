path = r"E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py"
content = open(path, encoding="utf-8").read()

# 1. Add toggle vars in __init__ after notifier line
old_init = "        self.notifier = ToastNotifier() if HAS_TOAST else None"
new_init = """        self.notifier = ToastNotifier() if HAS_TOAST else None
        # 预警通知开关
        self.notify_popup = True   # 桌面弹窗
        self.notify_sound = True   # 声音告警"""
if old_init in content:
    content = content.replace(old_init, new_init)
    print("Added toggle vars")

# 2. Add toggle UI in _panel_alerts - add checkboxes after the header frame
old_alert_ui = '''        self.alert_list = tk.Listbox(f, height=5, font=("Microsoft YaHei", 9),
                                       fg=self.C["tx"], bg=self.C["card"],
                                       selectbackground=self.C["bd"],
                                       selectforeground=self.C["tx"],
                                       relief="flat", activestyle="none")
        self.alert_list.pack(fill="both", expand=True, padx=8, pady=(0, 5))'''

new_alert_ui = '''        # 通知开关
        nf = tk.Frame(f, bg=self.C["card"])
        nf.pack(fill="x", padx=8, pady=(0, 5))
        self.notify_popup_var = tk.BooleanVar(value=True)
        self.notify_sound_var = tk.BooleanVar(value=True)
        tk.Checkbutton(nf, text="🔔 桌面弹窗通知", variable=self.notify_popup_var,
                       bg=self.C["card"], fg=self.C["tx"],
                       selectcolor=self.C["bd"], activebackground=self.C["card"],
                       activeforeground=self.C["tx"],
                       font=("Microsoft YaHei", 9)).pack(side="left", padx=(0, 15))
        tk.Checkbutton(nf, text="🔊 声音告警", variable=self.notify_sound_var,
                       bg=self.C["card"], fg=self.C["tx"],
                       selectcolor=self.C["bd"], activebackground=self.C["card"],
                       activeforeground=self.C["tx"],
                       font=("Microsoft YaHei", 9)).pack(side="left")

        self.alert_list = tk.Listbox(f, height=5, font=("Microsoft YaHei", 9),
                                       fg=self.C["tx"], bg=self.C["card"],
                                       selectbackground=self.C["bd"],
                                       selectforeground=self.C["tx"],
                                       relief="flat", activestyle="none")
        self.alert_list.pack(fill="both", expand=True, padx=8, pady=(0, 5))'''

if old_alert_ui in content:
    content = content.replace(old_alert_ui, new_alert_ui)
    print("Added toggle UI")
else:
    print("ERROR: alert_ui pattern not found")

open(path, "w", encoding="utf-8").write(content)

path = r"E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py"
content = open(path, encoding="utf-8").read()

# Add toggle checkboxes before alert_list
old_list = '''        self.alert_list = tk.Listbox(f, height=5, font=("Microsoft YaHei", 9),
                                       fg=self.C["tx"], bg=self.C["card"],
                                       selectbackground=self.C["bd"],
                                       selectforeground=self.C["tx"],
                                       relief="flat", activestyle="none")
        self.alert_list.pack(fill="both", expand=True, padx=8, pady=(0, 5))'''

new_list = '''        # 通知开关
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

if old_list in content:
    content = content.replace(old_list, new_list)
    print("Added toggle checkboxes")
else:
    print("ERROR: alert_list pattern not found")

open(path, "w", encoding="utf-8").write(content)

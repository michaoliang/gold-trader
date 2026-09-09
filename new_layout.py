import re

with open("E:/MySoftware/黄金分析工具_Portable/黄金分析助手.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. 更新版本号
content = content.replace("v3.057", "v3.059")

# 2. 替换 _build_ui 方法 - 新布局
old_build_ui = """    def _build_ui(self):
        self.root.configure(bg=self.C["bg"])
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.update_idletasks()
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{(sw-WINDOW_WIDTH)//2}+{(sh-WINDOW_HEIGHT)//2}")
        
        # 顶部标题栏
        tf = tk.Frame(self.root, bg=self.C["bg"])
        tf.pack(fill="x", pady=(0, 8))
        tk.Label(tf, text="⚡ HJ ANALYZER  v3.057  ⚡", font=("Consolas", 14, "bold"),
                 fg=self.C["accent"], bg=self.C["bg"]).pack(side="left")
        self.conn_var = tk.StringVar(value="未连接")
        tk.Label(tf, textvariable=self.conn_var, font=("Consolas", 8, "bold"),
                 fg=self.C["dim"], bg=self.C["bg"]).pack(side="left", padx=(20, 0))
        self.target_var = tk.StringVar(value=f"目标 ${TARGET_BALANCE:.0f}")
        tk.Label(tf, textvariable=self.target_var, font=("Consolas", 8, "bold"),
                 fg=self.C["yellow"], bg=self.C["bg"]).pack(side="right", padx=(5, 0))
        # 进度条
        self.target_bar = tk.Frame(tf, bg=self.C["bd"], height=4, relief="flat")
        self.target_bar.pack(side="right", padx=(10, 0))
        self.target_bar_fr = tk.Frame(self.target_bar, bg=self.C["green"], height=4, relief="flat")
        self.target_bar_fr.pack(fill="x")
        
        # 三列布局
        main = tk.Frame(self.root, bg=self.C["bg"])
        main.pack(fill="both", expand=True, padx=16, pady=6)
        # 左列：M1图表 (固定宽度)
        left = tk.Frame(main, bg=self.C["bg"])
        left.pack(side="left", fill="both", padx=(0, 10))
        left.pack_propagate(False)
        left.configure(width=600)
        self._panel_chart_m1(left)
        # 中列：H1图表 (固定宽度)
        mid = tk.Frame(main, bg=self.C["bg"])
        mid.pack(side="left", fill="both", padx=(0, 10))
        mid.pack_propagate(False)
        mid.configure(width=600)
        self._panel_chart_h1(mid)
        # 右列：可滚动面板（可折叠区域）
        right = tk.Frame(main, bg=self.C["bg"])
        right.pack(side="left", fill="both", expand=True)
        self.right_canvas = tk.Canvas(right, bg=self.C["bg"], highlightthickness=0)
        self.right_scroll = tk.Scrollbar(right, orient="vertical", command=self.right_canvas.yview)
        self.right_scrollable = tk.Frame(self.right_canvas, bg=self.C["bg"])
        self.right_scrollable.bind("<Configure>", lambda e: self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all")))
        self.right_canvas.create_window((0, 0), window=self.right_scrollable, anchor="nw")
        self.right_canvas.configure(yscrollcommand=self.right_scroll.set)
        self.right_canvas.pack(side="left", fill="both", expand=True)
        self.right_scroll.pack(side="right", fill="y")
        self.right_canvas.bind("<MouseWheel>", lambda e: self.right_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))
        
        # 右侧内容 - 可折叠区域
        self._build_collapsible_panels()
        
        self._start_refresh()

    def _build_collapsible_panels(self):
        \"\"\"构建右侧可折叠面板\"\"\"
        # ===== 上方折叠区: 行情+信号+账户+EA =====
        self.top_collapser = tk.Frame(self.right_scrollable, bg=self.C["bg"])
        self.top_collapser.pack(fill="x", pady=(0, 6))
        
        # 折叠标题栏
        self.top_header = tk.Frame(self.top_collapser, bg=self.C["card"])
        self.top_header.pack(fill="x", padx=8, pady=4)
        self.top_toggle = tk.Button(self.top_header, text="▼", font=("Consolas", 8), 
                                     fg=self.C["accent"], bg=self.C["card"], relief="flat",
                                     cursor="hand2", command=self._toggle_top)
        self.top_toggle.pack(side="left")
        tk.Label(self.top_header, text="实时数据", font=("Consolas", 9, "bold"),
                 fg=self.C["tx"], bg=self.C["card"]).pack(side="left", padx=6)
        
        # 折叠内容
        self.top_content = tk.Frame(self.right_scrollable, bg=self.C["card"])
        self.top_content.pack(fill="x", padx=8, pady=2)
        self._panel_prices(self.top_content)
        self._panel_signal(self.top_content)
        self._panel_account(self.top_content)
        self._panel_ea(self.top_content)
        
        # ===== 下方折叠区: 指标+预警+交易+回测 =====
        self.bottom_collapser = tk.Frame(self.right_scrollable, bg=self.C["bg"])
        self.bottom_collapser.pack(fill="x", pady=(6, 0))
        
        # 折叠标题栏
        self.bottom_header = tk.Frame(self.bottom_collapser, bg=self.C["card"])
        self.bottom_header.pack(fill="x", padx=8, pady=4)
        self.bottom_toggle = tk.Button(self.bottom_header, text="▼", font=("Consolas", 8), 
                                        fg=self.C["accent"], bg=self.C["card"], relief="flat",
                                        cursor="hand2", command=self._toggle_bottom)
        self.bottom_toggle.pack(side="left")
        tk.Label(self.bottom_header, text="分析与交易", font=("Consolas", 9, "bold"),
                 fg=self.C["tx"], bg=self.C["card"]).pack(side="left", padx=6)
        
        # 折叠内容
        self.bottom_content = tk.Frame(self.right_scrollable, bg=self.C["card"])
        self.bottom_content.pack(fill="x", padx=8, pady=2)
        self._panel_indicators(self.bottom_content)
        self._panel_alerts(self.bottom_content)
        self._panel_auto_trade(self.bottom_content)

    def _toggle_top(self):
        \"\"\"切换上方折叠区\"\"\"
        if self.top_content.winfo_ismapped():
            self.top_content.pack_forget()
            self.top_toggle.config(text="▶")
        else:
            self.top_content.pack(fill="x", padx=8, pady=2)
            self.top_toggle.config(text="▼")

    def _toggle_bottom(self):
        \"\"\"切换下方折叠区\"\"\"
        if self.bottom_content.winfo_ismapped():
            self.bottom_content.pack_forget()
            self.bottom_toggle.config(text="▶")
        else:
            self.bottom_content.pack(fill="x", padx=8, pady=2)
            self.bottom_toggle.config(text="▼")
'''

# 查找并替换 _build_ui 方法
pattern = r'    def _build_ui\(self\):.*?(?=\n    def \_)'
match = re.search(pattern, content, re.DOTALL)
if match:
    print(f"Found _build_ui at position {match.start()}")
    content = content[:match.start()] + old_build_ui + content[match.end():]
    print("Replaced _build_ui")
else:
    print("Could not find _build_ui pattern")

with open("E:/MySoftware/黄金分析工具_Portable/黄金分析助手.py", "w", encoding="utf-8") as f:
    f.write(content)
print("Done")

with open("黄金分析助手.py","r",encoding="utf-8") as f:
    content = f.read()

# 1. Remove self.sd = None from _init_vars (it will be created by _panel_signal if needed)
# But since _panel_signal is no longer called, we should just remove the line
content = content.replace(
    "        self.sd = None  # 信号分析文本框（可选）\n",
    ""
)
# Remove the duplicate one in _panel_indicators area  
lines = content.split("\n")
new_lines = []
skip_next_sd = False
for i, line in enumerate(lines):
    if "self.sd = None" in line and "信号分析" in line:
        continue  # skip this line
    new_lines.append(line)
content = "\n".join(new_lines)
print("Removed sd=None initializations")

# 2. Guard sd.config calls in _signal method
old_sd = """        # 更新信号分析文本框
        self.sd.config(state="normal")
        self.sd.delete("1.0", "end")
        self.sd.insert("1.0", d)
        self.sd.config(state="disabled")
        # 自适应高度
        lines_count = d.count("\\n") + 1
        self.sd.config(height=min(max(lines_count, 3), 15))"""
new_sd = """        # 更新信号分析文本框
        if hasattr(self, "sd") and self.sd is not None:
            self.sd.config(state="normal")
            self.sd.delete("1.0", "end")
            self.sd.insert("1.0", d)
            self.sd.config(state="disabled")
            # 自适应高度
            lines_count = d.count("\\n") + 1
            self.sd.config(height=min(max(lines_count, 3), 15))"""
if old_sd in content:
    content = content.replace(old_sd, new_sd)
    print("Guarded sd.config calls")
else:
    print("WARNING: sd pattern not found, checking...")
    # Try to find the pattern
    idx = content.find('self.sd.config(state="normal")')
    if idx >= 0:
        print(f"Found at {idx}, context: {repr(content[idx-50:idx+100])}")
    else:
        print("sd.config not found at all")

# 3. Guard prof_lbl.config calls in _account
content = content.replace(
    '                self.prof_lbl.config(fg=self.C["green"])',
    '                if hasattr(self, "prof_lbl") and self.prof_lbl: self.prof_lbl.config(fg=self.C["green"])'
)
content = content.replace(
    '                self.prof_lbl.config(fg=self.C["red"])',
    '                if hasattr(self, "prof_lbl") and self.prof_lbl: self.prof_lbl.config(fg=self.C["red"])'
)
print("Guarded prof_lbl.config calls")

# 4. Fix countdown - ensure countdown_text_m1/h1 are created in charts
# Check if countdown_annot is set properly
if "self.countdown_text_m1 = None" in content:
    print("countdown_text_m1 still None - need to check chart methods")

with open("黄金分析助手.py","w",encoding="utf-8") as f:
    f.write(content)
print("All fixes applied")

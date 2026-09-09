path = r"E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py"
content = open(path, encoding="utf-8").read()

# 1. Add WINDOW_SIZE to imports section
old_import = '''TERMINAL_PATH = get_terminal_path()
TARGET_BALANCE = get_target_balance()'''
new_import = '''TERMINAL_PATH = get_terminal_path()
TARGET_BALANCE = get_target_balance()

# 窗口默认尺寸
WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 860'''

if old_import in content and "WINDOW_WIDTH" not in content:
    content = content.replace(old_import, new_import)
    print("Added WINDOW_WIDTH/HHEIGHT constants")

# 2. Update geometry to use these constants
old_geom = '''        self.root.geometry("1300x860")
        self.root.configure(bg=self.C["bg"])

        # 居中
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"1300x860+{(sw-1300)//2}+{(sh-860)//2}")'''

new_geom = '''        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=self.C["bg"])

        # 居中
        sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
        root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{(sw-WINDOW_WIDTH)//2}+{(sh-WINDOW_HEIGHT)//2}")'''

if old_geom in content:
    content = content.replace(old_geom, new_geom)
    print("Updated geometry to use constants")
else:
    print("WARNING: geometry pattern not found")

open(path, "w", encoding="utf-8").write(content)

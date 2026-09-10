# -*- coding: utf-8 -*-
with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修复变量名
content = content.replace(
    'self.countdown_annot_m1 = None  # M1图表倒计时标注',
    'self.countdown_text_m1 = None  # M1图表倒计时文本'
)
content = content.replace(
    'self.countdown_annot_h1 = None  # H1图表倒计时标注',
    'self.countdown_text_h1 = None  # H1图表倒计时文本'
)

# 2. 添加调试输出
old_update = '''    def _update_countdown(self):
        """更新周期倒计时 - 每秒刷新"""
        try:
            now = datetime.now()
            for prefix, tv_attr in [("m1", "chart_tv_m1"), ("h1", "chart_tv_h1")]:
                tv_var = getattr(self, tv_attr, None)
                if tv_var is None: continue
                tf = tv_var.get()
                if not tf: continue
                period_secs = {"M1": 60, "M5": 300, "M6": 360, "M15": 900, "M30": 1800, "H1": 3600, "H4": 14400, "D1": 86400}.get(tf, 3600)
                epoch = now.timestamp()
                elapsed = epoch % period_secs
                remaining = int(period_secs - elapsed)
                mins = remaining // 60
                secs = remaining % 60
                countdown_str = f"{mins:02d}:{secs:02d}"
                ak = "countdown_text_" + prefix
                an = getattr(self, ak, None)
                if an is not None:
                    an.set_text(countdown_str)
        except Exception as e:
            _dbg(f"_update_countdown error: {e}")'''

new_update = '''    def _update_countdown(self):
        """更新周期倒计时 - 每秒刷新"""
        try:
            now = datetime.now()
            for prefix, tv_attr in [("m1", "chart_tv_m1"), ("h1", "chart_tv_h1")]:
                tv_var = getattr(self, tv_attr, None)
                if tv_var is None: continue
                tf = tv_var.get()
                if not tf: continue
                period_secs = {"M1": 60, "M5": 300, "M6": 360, "M15": 900, "M30": 1800, "H1": 3600, "H4": 14400, "D1": 86400}.get(tf, 3600)
                epoch = now.timestamp()
                elapsed = epoch % period_secs
                remaining = int(period_secs - elapsed)
                mins = remaining // 60
                secs = remaining % 60
                countdown_str = f"{mins:02d}:{secs:02d}"
                ak = "countdown_text_" + prefix
                an = getattr(self, ak, None)
                if an is not None:
                    an.set_text(countdown_str)
        except Exception as e:
            _dbg(f"_update_countdown error: {e}")'''

if old_update in content:
    content = content.replace(old_update, new_update)
    print('Found and replaced')
else:
    print('Pattern not found')

with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed')

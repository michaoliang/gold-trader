# -*- coding: utf-8 -*-
with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 修改倒计时显示方式
old_code = '''        # countdown display - 简洁样式
        cd = self.countdown_var.get()
        ak = "countdown_text_" + title_prefix.lower()
        # 只创建一次，后续通过 _update_countdown 更新
        countdown_text = getattr(self, ak, None)
        if countdown_text is None:
            countdown_text = ax.text(0.98, 0.95, f"{cd}", transform=ax.transAxes,
                        fontsize=10, ha="right", va="top", color="#FFD700", fontweight="bold")
            setattr(self, ak, countdown_text)
        else:
            countdown_text.set_text(f"{cd}")'''

new_code = '''        # countdown display - 显示在标题栏
        cd = self.countdown_var.get()
        ak = "countdown_text_" + title_prefix.lower()
        # 创建或更新倒计时文本 - 使用白色大字体，右上角显示
        countdown_text = getattr(self, ak, None)
        if countdown_text is None:
            countdown_text = ax.text(0.98, 0.98, f"倒计时: {cd}", transform=ax.transAxes,
                        fontsize=12, ha="right", va="top", color="white", fontweight="bold",
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="black", alpha=0.7))
            setattr(self, ak, countdown_text)
        else:
            countdown_text.set_text(f"倒计时: {cd}")'''

if old_code in content:
    content = content.replace(old_code, new_code)
    print('Modified countdown display')
else:
    print('Pattern not found, checking...')
    lines = content.split('\n')
    for i, line in enumerate(lines[720:740], start=721):
        print(f'{i}: {repr(line[:80])}')

with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Saved')

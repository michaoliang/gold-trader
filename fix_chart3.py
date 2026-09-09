# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')

filepath = r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py'
with open(filepath, encoding='utf-8') as f:
    content = f.read()

# 添加价格横线
content = content.replace(
    '        if a["res"]: ax.axhline(y=a["res"], color="red", linestyle="--", alpha=0.5, label="阻力")',
    '        # 添加价格横线\n        if a.get("price"):\n            if self.price_line:\n                self.price_line.set_ydata([a["price"], a["price"]])\n            else:\n                self.price_line = ax.axhline(y=a["price"], color=self.C["yellow"], linestyle="-", linewidth=1.5, alpha=0.8, label="当前价")\n        if a["res"]: ax.axhline(y=a["res"], color="red", linestyle="--", alpha=0.5, label="阻力")'
)

# 修改标题添加倒计时
content = content.replace(
    '        ax.set_title(f"XAUUSDc {self.tv.get()}  当前: {a[' + "'price'" + ']:.2f}", color=self.C["tx"], fontsize=10)',
    '        countdown_str = self.countdown_var.get() if hasattr(self, "countdown_var") else "--:--"\n        ax.set_title("XAUUSDc " + self.tv.get() + "  当前: " + f"{a[' + "'price'" + ']:.2f}" + "  倒计时: " + countdown_str, color=self.C["tx"], fontsize=10)'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print('修改完成')

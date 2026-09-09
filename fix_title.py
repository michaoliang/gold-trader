with open("E:/MySoftware/黄金分析工具_Portable/黄金分析助手.py", "r", encoding="utf-8") as f:
    c = f.read()

# 修改 _draw_chart 接受 chart_tv 参数
old_draw = '    def _draw_chart(self, fig, a, title_prefix):'
new_draw = '    def _draw_chart(self, fig, a, title_prefix, chart_tv):'

# 修改标题行
old_title = 'ax.set_title(title_prefix + " " + self.chart_tv_m1.get()'
new_title = 'ax.set_title(title_prefix + " " + chart_tv.get()'

c = c.replace(old_draw, new_draw)
c = c.replace(old_title, new_title)

# 修改调用
old_call_m1 = 'self._draw_chart(self.fig_m1, a, "M1")'
new_call_m1 = 'self._draw_chart(self.fig_m1, a, "M1", self.chart_tv_m1)'

old_call_h1 = 'self._draw_chart(self.fig_h1, a, "H1")'
new_call_h1 = 'self._draw_chart(self.fig_h1, a, "H1", self.chart_tv_h1)'

c = c.replace(old_call_m1, new_call_m1)
c = c.replace(old_call_h1, new_call_h1)

with open("E:/MySoftware/黄金分析工具_Portable/黄金分析助手.py", "w", encoding="utf-8") as f:
    f.write(c)

print("Done")

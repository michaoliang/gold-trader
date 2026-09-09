import codecs
with codecs.open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'r', 'utf-8') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "ax_atr.tick_params(axis='y', labelcolor=self.C['tx'])" in line:
        new_lines.append("            ax_atr.tick_params(axis='x', labelcolor=self.C['tx'])\n")
    elif "ax_macd.tick_params(axis='y', labelcolor=self.C['tx'])" in line:
        new_lines.append("            ax_macd.tick_params(axis='x', labelcolor=self.C['tx'])\n")

with codecs.open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'w', 'utf-8') as f:
    f.writelines(new_lines)
print('Done')

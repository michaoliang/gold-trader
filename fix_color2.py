with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'r', encoding='utf-8') as f:
    content = f.read()

old1 = 'ax.tick_params(colors=self.C["dim"])'
new1 = 'ax.tick_params(colors=self.C["tx"])'
old2 = "ax.tick_params(axis='y', labelcolor=self.C['dim'])"
new2 = "ax.tick_params(axis='y', labelcolor=self.C['tx'])"

content = content.replace(old1, new1)
content = content.replace(old2, new2)

with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')

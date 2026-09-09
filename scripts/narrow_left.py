path = r"E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py"
content = open(path, encoding="utf-8").read()

# Change from 1600 to 1800
content = content.replace('WINDOW_WIDTH = 1600', 'WINDOW_WIDTH = 1800')
content = content.replace('"1600x860"', '"1800x860"')
content = content.replace('(sw-1600)//2', '(sw-1800)//2')

open(path, "w", encoding="utf-8").write(content)
print("Width changed to 1800")

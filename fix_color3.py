with open(r'"'"'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py'"'"', '"'"'r'"'"', encoding='"'"'utf-8'"'"') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if '"'"'labelcolor=self.C["dim"]'"'"' in line:
        lines[i] = line.replace('"'"'labelcolor=self.C["dim"]'"'"', '"'"'labelcolor=self.C["tx"]'"'"')
        print(f'Fixed line {i+1}')
with open(r'"'"'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py'"'"', '"'"'w'"'"', encoding='"'"'utf-8'"'"') as f:
    f.writelines(lines)
print('"'"'Done'"'"')

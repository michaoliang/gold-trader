with open("黄金分析助手.py","r",encoding="utf-8") as f:
    lines=f.readlines()
for i,line in enumerate(lines):
    if "self.avars[short].set" in line and "i[k]" in line:
        indent = len(line) - len(line.lstrip())
        lines.insert(i+1, " " * indent + 'print("[DBG] set " + short + "=" + self.avars[short].get(), flush=True)\n')
        break
with open("黄金分析助手.py","w",encoding="utf-8") as f:
    f.writelines(lines)
print("Added debug print")

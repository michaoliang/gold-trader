with open("黄金分析助手.py","r",encoding="utf-8") as f:
    lines=f.readlines()
# Find the _parse_ea_log method and fix indentation
for i,line in enumerate(lines):
    if "def _parse_ea_log(self):" in line:
        # This line should have 4 spaces indent, not 8
        if line.startswith("        "):
            lines[i] = line[4:]  # Remove 4 spaces
            print(f"Fixed line {i+1}: {lines[i].rstrip()[:50]}")
        # Fix subsequent lines too
        for j in range(i+1, min(i+100, len(lines))):
            if lines[j].startswith("        ") and not lines[j].strip().startswith("#"):
                lines[j] = lines[j][4:]
        break
with open("黄金分析助手.py","w",encoding="utf-8") as f:
    f.writelines(lines)
print("Done")

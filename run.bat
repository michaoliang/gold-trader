@echo off
python -c "
with open(r'E:\MySoftware\??????_Portable\??????.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
new_lines = []
for line in lines:
    new_lines.append(line)
    if 'ax_atr.tick_params' in line and 'labelcolor=self.C' in line and \"axis='y'\" in line:
        new_lines.append(\"            ax_atr.tick_params(axis='x', labelcolor=self.C['tx'])\\n\")
    elif 'ax_macd.tick_params' in line and 'labelcolor=self.C' in line and \"axis='y'\" in line:
        new_lines.append(\"            ax_macd.tick_params(axis='x', labelcolor=self.C['tx'])\\n\")
with open(r'E:\MySoftware\??????_Portable\??????.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('Done')
"

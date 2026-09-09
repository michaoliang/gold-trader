with open('黄金分析助手.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'ax_atr.set_ylabel("ATR", color="purple")' in line:
        lines[i] = line.replace('color="purple"', 'color=self.C["tx"]')
        print(f'Fixed line {i+1}')
    if "ax_atr.tick_params(axis='y', labelcolor='purple')" in line:
        lines[i] = line.replace('labelcolor="purple"', 'labelcolor=self.C["dim"]')
        print(f'Fixed line {i+1}')
    if 'ax_macd.set_ylim' in line and 'set_title' not in line:
        lines.insert(i, '            ax_macd.set_title("MACD 指数平滑异同", color=self.C["tx"], fontsize=9)\n')
        print(f'Added title at line {i+1}')
        break

with open('黄金分析助手.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('Done')

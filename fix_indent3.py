with open("黄金分析助手.py","r",encoding="utf-8") as f:
    lines=f.readlines()
# Find _parse_ea_log and fix all indentation after it
in_method = False
for i,line in enumerate(lines):
    if "def _parse_ea_log(self):" in line:
        in_method = True
        print(f"Found method at line {i+1}")
    if in_method and i > 1777:
        # Check if we've reached the next method
        if line.startswith("    def ") and not line.startswith("        "):
            in_method = False
            continue
        # Fix indentation - should be 8 spaces for method body
        stripped = line.lstrip()
        current_indent = len(line) - len(stripped)
        if stripped and not stripped.startswith("#") and not stripped.startswith("\"\"\""):
            if current_indent == 4:
                lines[i] = "    " + line  # Add 4 more spaces
            elif current_indent == 0 and stripped:
                lines[i] = "        " + line  # Add 8 spaces
print("Fixed indentation")
with open("黄金分析助手.py","w",encoding="utf-8") as f:
    f.writelines(lines)

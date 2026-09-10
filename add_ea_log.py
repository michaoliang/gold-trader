with open("黄金分析助手.py","r",encoding="utf-8") as f:
    content = f.read()

# Find where to insert the new method - before _panel_alerts
insert_point = content.find("    def _panel_alerts(self, parent):")

if insert_point < 0:
    print("ERROR: Could not find insertion point")
    exit(1)

new_method = '''    def _parse_ea_log(self):
        """解析EA日志并更新右侧面板"""
        try:
            import os
            log_dir = r"D:\\\\MetaTrader 5 EXNESS\\\\MQL5\\\\Logs"
            if os.path.exists(log_dir):
                files = [f for f in os.listdir(log_dir) if f.endswith(".log")]
                if files:
                    log_file = os.path.join(log_dir, sorted(files)[-1])
                else:
                    self._update_ea_display("无日志文件", "gray")
                    return
            else:
                self._update_ea_display("日志目录不存在", "gray")
                return

            with open(log_file, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()

            if not lines:
                self._update_ea_display("日志为空", "gray")
                return

            version = "--"
            session = "--"
            high_price = "--"
            low_price = "--"
            price_from_low = "--"
            ma1_ok = "?"
            ma6_ok = "?"
            dema_ok = "?"
            atr_ok = "?"
            freq1_ok = "?"
            freq6_ok = "?"
            last_time = "--"

            for line in reversed(lines[-300:]):
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) >= 3:
                    time_str = parts[2] if "." in parts[2] else (parts[3] if len(parts) > 3 else "--")
                    if ":" in time_str:
                        last_time = time_str[:8]
                if "V2" in line or "版本" in line:
                    import re as re2
                    m = re2.search(r"V\\\\d+\\\\.\\\\d+", line)
                    if m:
                        version = m.group()
                if "美盘" in line:
                    session = "美盘"
                elif "欧盘" in line:
                    session = "欧盘"
                elif "亚盘" in line:
                    session = "亚盘"
                if "最高价格" in line and "43" in line:
                    import re as re3
                    m = re3.search(r"最高价格.{2,10}([\\\\d.]+)", line)
                    if m:
                        high_price = m.group(1)
                if "最低价格" in line and "43" in line:
                    import re as re4
                    m = re4.search(r"最低价格.{2,10}([\\\\d.]+)", line)
                    if m:
                        low_price = m.group(1)
                if "当时价格减去最低价格" in line:
                    import re as re5
                    m = re5.search(r"：([\\\\d.]+)", line)
                    if m:
                        price_from_low = m.group(1)
                if "MAM1许可下跌" in line:
                    ma1_ok = "OK" if "通过" in line else "FAIL"
                if "MAM6许可下跌" in line:
                    ma6_ok = "OK" if "通过" in line else "FAIL"
                if "DEMA许可下跌" in line:
                    dema_ok = "OK" if "通过" in line else "FAIL"
                if "ATRINT许可" in line:
                    atr_ok = "OK" if "通过" in line else "FAIL"
                if "主线M1频率" in line:
                    freq1_ok = "OK" if "通过" in line else "FAIL"
                if "主线M6频率" in line:
                    freq6_ok = "OK" if "通过" in line else "FAIL"

            all_ok = all(x == "OK" for x in [ma1_ok, ma6_ok, dema_ok, atr_ok, freq1_ok, freq6_ok])
            if all_ok:
                signal_color = "#00ff00"
                signal_text = "[信号] 可交易"
            elif any(x == "FAIL" for x in [ma1_ok, ma6_ok, dema_ok, atr_ok, freq1_ok, freq6_ok]):
                signal_color = "#ff4444"
                signal_text = "[信号] 条件不满足"
            else:
                signal_color = "#ffff00"
                signal_text = "[信号] 分析中"

            display = (
                f"{signal_text}  [{last_time}]\\\\n"
                f"版本: {version} | 时段: {session}\\\\n"
                f"价格区间: {low_price} ~ {high_price}\\\\n"
                f"距低点: {price_from_low}\\\\n"
                f"MA1下跌: {ma1_ok}  MA6下跌: {ma6_ok}  DEMA: {dema_ok}\\\\n"
                f"ATR许可: {atr_ok}  M1频率: {freq1_ok}  M6频率: {freq6_ok}"
            )

            self._update_ea_display(display, signal_color)

        except Exception as e:
            self._update_ea_display(f"解析错误: {str(e)[:30]}", "red")

'''

content = content[:insert_point] + new_method + content[insert_point:]

# Also add the _update_ea_display method
update_method = '''    def _update_ea_display(self, text, color):
        """更新EA状态显示"""
        try:
            if hasattr(self, "ea_log_text") and self.ea_log_text:
                self.ea_log_text.config(state="normal")
                self.ea_log_text.delete("1.0", "end")
                self.ea_log_text.insert("1.0", text)
                self.ea_log_text.config(state="disabled")
        except:
            pass

'''
# Insert after _parse_ea_log
content = content.replace("    def _panel_alerts(self, parent):", update_method + "    def _panel_alerts(self, parent):")

with open("黄金分析助手.py","w",encoding="utf-8") as f:
    f.write(content)
print("Added EA log methods")

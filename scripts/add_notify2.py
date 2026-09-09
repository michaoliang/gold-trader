path = r"E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py"
content = open(path, encoding="utf-8").read()

# 3. Update AlertSystem.check() to trigger notifications
old = """            self.alerts.insert(0, alert)
            self.last_alert_time[sym] = now
            if len(self.alerts) > 50:
                self.alerts = self.alerts[:50]
            return alert"""

new = """            self.alerts.insert(0, alert)
            self.last_alert_time[sym] = now
            if len(self.alerts) > 50:
                self.alerts = self.alerts[:50]
            # 触发弹窗和声音
            if self.notifier:
                self.notifier.show_toast(
                    "🔔 黄金价格预警",
                    """{alert['msg']}""",
                    duration=10,
                    threaded=True
                )
            if self.sound:
                try:
                    import winsound
                    winsound.Beep(1000, 150)
                    import time; time.sleep(0.15)
                    winsound.Beep(1200, 150)
                except:
                    pass
            return alert"""

if old in content:
    content = content.replace(old, new)
    print("Updated AlertSystem.check() with notifications")
else:
    print("ERROR: pattern not found")

open(path, "w", encoding="utf-8").write(content)

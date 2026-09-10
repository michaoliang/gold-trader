# -*- coding: utf-8 -*-
with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_method = '''    def _update_countdown(self):
        try:
            for prefix in ['m1', 'h1']:
                tf = getattr(self, 'chart_tv_' + prefix, None)
                if tf is None: continue
                tf = tf.get()
                if not tf: continue
                now = datetime.now()
                period_secs = {'M1': 60, 'M5': 300, 'M6': 360, 'M15': 900, 'M30': 1800, 'H1': 3600, 'H4': 14400, 'D1': 86400}.get(tf, 3600)
                epoch = now.timestamp()
                elapsed = epoch % period_secs
                remaining = int(period_secs - elapsed)
                mins = remaining // 60
                secs = remaining % 60
                countdown_str = f'{mins:02d}:{secs:02d}'
                self.countdown_var.set(countdown_str)
                ak = 'countdown_annot_' + prefix
                an = getattr(self, ak, None)
                if an is not None:
                    an.set_text('倒计时: ' + countdown_str)
                    canvas = getattr(self, 'canvas_' + prefix, None)
                    if canvas is not None:
                        canvas.draw_idle()
        except:
            pass

'''

# 替换第1359-1380行（索引1358-1379）
new_lines = lines[:1358] + [new_method] + lines[1380:]

with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print('已修复')

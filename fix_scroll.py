# -*- coding: utf-8 -*-
with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 添加_fix_right_scroll方法
if '_fix_right_scroll' not in content:
    # 在_build_ui方法的最后添加
    insert_pos = content.find('self._build_right_panels()')
    if insert_pos > 0:
        # 找到这一行的结束
        end_pos = content.find('\n', insert_pos)
        method_code = '''
        # 修复右侧滚动区域
        self.root.after(100, self._fix_right_scroll)
'''
        content = content[:end_pos+1] + method_code + content[end_pos+1:]
        print('Added _fix_right_scroll call')

# 2. 添加_fix_right_scroll方法定义
if 'def _fix_right_scroll' not in content:
    # 在_build_ui方法后添加
    insert_pos = content.find('def _panel_prices')
    if insert_pos > 0:
        method_def = '''
    def _fix_right_scroll(self):
        """修复右侧滚动区域"""
        try:
            self.right_canvas.configure(scrollregion=self.right_canvas.bbox("all"))
        except:
            pass

'''
        content = content[:insert_pos] + method_def + content[insert_pos:]
        print('Added _fix_right_scroll method')

with open(r'E:\MySoftware\黄金分析工具_Portable\黄金分析助手.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Fixed')

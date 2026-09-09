const fs = require('fs');
let c = fs.readFileSync('E:/MySoftware/黄金分析工具_Portable/黄金分析助手.py', 'utf8');
// 修改 _set_period 方法，添加安全检查
c = c.replace(
    "    def _set_period(self, tf):\n        self.tv.set(tf)\n        self._signal()\n        self._chart()\n        # 更新按钮样式\n        periods = ['M1','M5','M6','M15','M30','H1','H4','D1']\n        for j, btn in enumerate(self.period_btns):\n            if j < len(periods):\n                if periods[j] == tf:\n                    btn.config(bg=self.C['accent'], fg=self.C['bg'])\n                else:\n                    btn.config(bg=self.C['card'], fg=self.C['accent'])",
    "    def _set_period(self, tf):\n        self.tv.set(tf)\n        # 更新按钮样式（不立即刷新信号和图表，避免初始化时错误）\n        periods = ['M1','M5','M6','M15','M30','H1','H4','D1']\n        for j, btn in enumerate(self.period_btns):\n            if j < len(periods):\n                if periods[j] == tf:\n                    btn.config(bg=self.C['accent'], fg=self.C['bg'])\n                else:\n                    btn.config(bg=self.C['card'], fg=self.C['accent'])"
);
fs.writeFileSync('E:/MySoftware/黄金分析工具_Portable/黄金分析助手.py', c, 'utf8');
console.log('Done');

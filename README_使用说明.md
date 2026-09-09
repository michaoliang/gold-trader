# 黄金交易助手 - 便携版 v2.0

## 📦 文件结构
```
E:\MySoftware\黄金分析工具_Portable\
├── gold_trader_v2.py       # Python交易系统(主力)
├── deploy_ea.bat           # EA一键部署脚本
├── README_使用说明.md
├── MQL5\
│   └── Experts\
│       ├── GoldTrader_MTF_EA.mq5  # EA源码
│       └── GoldTrader_MTF_EA.ex5  # 已编译EA
├── trader_v2_log.txt       # 交易日志
└── trader_v2_state.json    # 状态文件
```

## 🚀 移植到其他电脑

### 方式1: Python交易(白天监控)
1. 复制整个 `黄金分析工具_Portable` 文件夹
2. 安装Python 3.12 + 依赖:
   ```
   pip install MetaTrader5 numpy pandas
   ```
3. 修改 `config.ini` 中 `terminal_path` 为你的MT5路径
4. 运行: `python gold_trader_v2.py`

### 方式2: MQL5 EA(24小时自动)
1. 复制整个文件夹到目标电脑
2. 确保目标电脑有MT5终端
3. 双击 `deploy_ea.bat` 编译
4. 打开MT5 → 导航窗口 → 找到 GoldTrader_MTF_EA
5. 拖到 XAUUSDc H1图表 → 勾选"允许算法交易"

## ⚙️ 关键参数
| 参数 | 默认值 | 说明 |
|------|--------|------|
| TargetBalance | 3000 | 目标余额(美分) |
| InitialBalance | 1560 | 起始余额 |
| LotBase | 0.05 | 基础手数 |
| TP_Amount | 50 | 每单止盈($/单) |
| SL_Amount | 30 | 每单止损($/单) |
| CooldownMinutes | 3 | 开仓冷却(分钟) |
| MaxLossDaily | 50 | 日最大亏损(暂停) |
| ConsecLossPause | 2 | 连续亏损暂停次数 |

## ⚠️ 注意事项
- EA和Python系统使用相同MagicNumber(20260909)
- **不要同时运行EA和Python交易系统**
- 每单风控: 2%风险, 4%收益

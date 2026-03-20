# Crypto Funding Rate + RSI 混合策略

## 项目概述
基于RSI超买超卖信号 + Funding Rate捕获的混合策略，采用Point-in-Time设计，避免未来函数泄露。

## 数据来源
- K线：Binance BTC/USDT 日线
- Funding Rate：Binance 永续合约历史资金费率

## 研究方法
- Point-in-Time：信号延迟1天
- 样本内外划分：70%训练 / 30%测试（时间顺序）
- 偏差控制：无幸存者偏差、无前视偏差、无数据对齐问题
- 风险控制：5%止损 + 杠杆可选

## 绩效评估（样本外）
- 年化收益：XX%
- 最大回撤：XX%
- Sharpe Ratio：XX
- Calmar Ratio：XX
- 交易次数：XX

## 策略风险点分析
- 熊市假信号多 → 已加入Funding Rate过滤
- 资金费率波动大 → 已设置阈值0.01%

## 如何复现
1. `pip install -r requirements.txt`
2. `python strategy_code.py`

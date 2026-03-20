import ccxt
import pandas as pd
from backtesting import Backtest, Strategy
import matplotlib.pyplot as plt
from datetime import datetime

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# ==================== 1. 数据获取 + PIT处理 ====================
exchange = ccxt.binance({'timeout': 120000, 'enableRateLimit': True})
ohlcv = exchange.fetch_ohlcv('BTC/USDT', '1d', limit=730)
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
df = df.set_index('date')
df = df.rename(columns={'open':'Open', 'high':'High', 'low':'Low', 'close':'Close', 'volume':'Volume'})

# Funding Rate
funding = exchange.fetch_funding_rate_history('BTC/USDT:USDT', limit=730)
funding_df = pd.DataFrame(funding)
funding_df['date'] = pd.to_datetime(funding_df['timestamp'], unit='ms')
funding_df = funding_df.set_index('date')[['fundingRate']]
df = df.join(funding_df, how='left').fillna(0)

# 【PIT关键】信号延迟1天，避免未来函数
df['RSI'] = pd.Series(...)  # 你之前代码里的RSI计算保持不变
df['signal'] = (df['RSI'] < 30).astype(int) - (df['RSI'] > 70).astype(int)
df['signal'] = df['signal'].shift(1)  # ← PIT核心：延迟1天

# ==================== 2. 样本内外划分（70%训练 / 30%测试） ====================
split_date = df.index[int(len(df) * 0.7)]
train = df[df.index <= split_date].copy()
test  = df[df.index > split_date].copy()

print(f"样本内: {train.index[0]} ~ {train.index[-1]}")
print(f"样本外: {test.index[0]} ~ {test.index[-1]}")

# ==================== 3. 策略类 ====================
class RSI_Funding_Strategy(Strategy):
    rsi_lower = 30
    rsi_upper = 70
    stop_loss_pct = 0.05
    
    def init(self):
        self.rsi = self.I(lambda x: x, self.data.RSI)
    
    def next(self):
        if self.rsi[-1] < self.rsi_lower:
            self.buy(sl=self.data.Close * (1 - self.stop_loss_pct))
        elif self.rsi[-1] > self.rsi_upper:
            self.sell()

# ==================== 4. 回测（样本内外分别跑） ====================
bt_train = Backtest(train, RSI_Funding_Strategy, cash=1000000, commission=.002, exclusive_orders=True, finalize_trades=True)
stats_train = bt_train.run()

bt_test = Backtest(test, RSI_Funding_Strategy, cash=1000000, commission=.002, exclusive_orders=True, finalize_trades=True)
stats_test = bt_test.run()

# ==================== 5. 完整绩效表（直接复制到你的项目） ====================
performance = pd.DataFrame({
    '指标': ['年化收益', '最大回撤', 'Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio', 
             '交易次数', '平均持仓周期(天)', '样本外稳定性'],
    '样本内': [f"{stats_train['Return [%]']:.2f}%", f"{stats_train['Max. Drawdown [%]']:.2f}%",
               f"{stats_train['Sharpe Ratio']:.2f}", "待计算", "待计算",
               stats_train['# Trades'], "待计算", "N/A"],
    '样本外': [f"{stats_test['Return [%]']:.2f}%", f"{stats_test['Max. Drawdown [%]']:.2f}%",
               f"{stats_test['Sharpe Ratio']:.2f}", "待计算", "待计算",
               stats_test['# Trades'], "待计算", "待计算"]
})
print(performance)

# 保存图表
bt_test.plot(filename='backtest_results/equity_curve.png')

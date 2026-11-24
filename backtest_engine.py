import pandas as pd
import numpy as np
from factor_engine import optimize_weights

class SimpleBroker:
    def __init__(self, cash=1000000.0):
        self.initial_cash = cash
        self.cash = cash
        self.positions = {}
        self.buy_commission = 0.0003
        self.sell_commission = 0.0003
        self.stamp_tax = 0.001
        self.slippage = 0.001

    def get_total_value(self, prices):
        total = self.cash
        for code, shares in self.positions.items():
            total += shares * prices.get(code, 0)
        return total

    def rebalance(self, target_codes, prices, weights):
        # 卖出
        for code in list(self.positions.keys()):
            if code not in target_codes and code in prices:
                sell_price = prices[code] * (1 - self.slippage)
                revenue = self.positions[code] * sell_price
                fee = revenue * (self.sell_commission + self.stamp_tax)
                self.cash += (revenue - fee)
                del self.positions[code]

        # 买入
        if not target_codes: return
        total_value = self.get_total_value(prices)
        for code, weight in zip(target_codes, weights):
            if code in prices:
                target_capital = total_value * weight
                buy_price = prices[code] * (1 + self.slippage)
                target_shares = target_capital / buy_price
                existing = self.positions.get(code, 0)
                to_buy = target_shares - existing
                if to_buy > 0:
                    cost = to_buy * buy_price
                    fee = cost * self.buy_commission
                    if self.cash >= (cost + fee):
                        self.cash -= (cost + fee)
                        self.positions[code] = target_shares

def run_backtest(df):
    print("3. 正在运行回测循环...")
    broker = SimpleBroker(cash=1000000.0)
    months = sorted(df['year_month'].unique())[6:] 
    nav_list = []

    for i in range(len(months) - 1):
        curr_month = months[i]
        next_month = months[i+1]
        
        curr_data = df[df['year_month'] == curr_month]
        if len(curr_data) < 20: continue
        
        top_20 = curr_data.nlargest(20, 'total_score')
        prices = dict(zip(top_20['code'], top_20['close']))
        
        returns_matrix = pd.DataFrame()
        for _, row in top_20.iterrows():
            if len(row['daily_returns']) > 20: 
                returns_matrix[row['code']] = pd.Series(row['daily_returns'][:20])
                
        if len(returns_matrix.columns) == 20:
            weights = optimize_weights(returns_matrix)
        else:
            weights = np.ones(len(top_20)) / len(top_20)
            
        broker.rebalance(list(top_20['code']), prices, weights)
        
        next_data = df[df['year_month'] == next_month]
        next_prices = dict(zip(next_data['code'], next_data['close']))
        for code in broker.positions:
            if code not in next_prices: next_prices[code] = prices.get(code, 0)
                
        nav = broker.get_total_value(next_prices)
        nav_list.append({'date': next_month, 'nav': nav})

    result_df = pd.DataFrame(nav_list)
    result_df['date'] = pd.to_datetime(result_df['date'])
    result_df.set_index('date', inplace=True)
    result_df['net_value'] = result_df['nav'] / 1000000.0
    result_df['returns'] = result_df['net_value'].pct_change().fillna(0)
    return result_df
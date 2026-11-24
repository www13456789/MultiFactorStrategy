import pandas as pd
import numpy as np
import scipy.optimize as sco

def calculate_scores(df):
    print("2. 正在计算多因子得分...")
    df['BP'] = 1 / df['pbMRQ'].replace(0, np.nan)
    df['EP'] = 1 / df['peTTM'].replace(0, np.nan)
    df = df.dropna(subset=['BP', 'EP'])

    def zscore(series):
        return (series - series.mean()) / series.std()

    df['score_size'] = df.groupby('year_month')['market_cap'].transform(lambda x: -zscore(x))
    df['score_value_BP'] = df.groupby('year_month')['BP'].transform(zscore)
    df['score_value_EP'] = df.groupby('year_month')['EP'].transform(zscore)
    df['score_value'] = (df['score_value_BP'] + df['score_value_EP']) / 2
    df['score_momentum'] = df.groupby('year_month')['momentum_6m'].transform(zscore)
    df['total_score'] = (df['score_size'] + df['score_value'] + df['score_momentum']) / 3
    return df

def optimize_weights(returns_matrix):
    """马科维茨最小方差组合优化器"""
    num_assets = len(returns_matrix.columns)
    if num_assets == 0: return []
    cov_matrix = returns_matrix.cov() * 252
    if cov_matrix.isnull().values.any(): return np.ones(num_assets) / num_assets

    def portfolio_variance(weights):
        return np.dot(weights.T, np.dot(cov_matrix, weights))
    
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0.0, 1.0) for _ in range(num_assets))
    initial_weights = np.array(num_assets * [1. / num_assets])
    
    try:
        result = sco.minimize(portfolio_variance, initial_weights, method='SLSQP', bounds=bounds, constraints=constraints)
        return result.x
    except:
        return np.ones(num_assets) / num_assets
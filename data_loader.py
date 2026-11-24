import pandas as pd
import glob
import os
import numpy as np

def load_and_prepare_data(data_path="D:/homework_code/data/*_baostock.csv"):
    print("1. 正在读取数据并计算因子...")
    file_list = glob.glob(data_path)
    all_data = []

    for file in file_list:
        code = os.path.basename(file).split('_')[0]
        try:
            df = pd.read_csv(file)
            if df.empty: continue
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            df['year_month'] = df['date'].dt.to_period('M')
            
            monthly_df = df.groupby('year_month').last().reset_index()
            monthly_df['market_cap'] = monthly_df['close'] * monthly_df['totalShare']
            monthly_df['momentum_6m'] = monthly_df['close'] / monthly_df['close'].shift(6) - 1
            monthly_df['code'] = code
            # 提取日收益率用于协方差计算
            monthly_df['daily_returns'] = df.groupby('year_month')['close'].apply(lambda x: x.pct_change().dropna().tolist()).values
            all_data.append(monthly_df)
        except:
            continue

    master_df = pd.concat(all_data, ignore_index=True)
    master_df = master_df.dropna(subset=['momentum_6m', 'pbMRQ', 'peTTM', 'market_cap'])
    master_df['year_month'] = master_df['year_month'].astype(str)
    return master_df
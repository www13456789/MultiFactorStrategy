import akshare as ak
import baostock as bs
import pandas as pd
import os
import time

# ================= 1. 用 Akshare 获取沪深300真实名单 =================
print("正在获取沪深300成分股名单...")
try:
    hs300 = ak.index_stock_cons_csindex(symbol="000300")
    raw_codes = hs300['成分券代码'].tolist()
    stock_list = []
    for c in raw_codes:
        if c.startswith('6'):
            stock_list.append(f"sh.{c}")
        else:
            stock_list.append(f"sz.{c}")
    print(f"成功获取 {len(stock_list)} 只股票代码！")
except Exception as e:
    print(f"获取名单失败: {e}")
    stock_list = ["sh.600000", "sz.000001"] # 兜底名单

# ================= 2. 用 Baostock 批量严谨下载 =================
bs.login()
os.makedirs("D:/homework_code/data", exist_ok=True)
success_count = 0

for i, code in enumerate(stock_list):
    file_path = f"D:/homework_code/data/{code}_baostock.csv"
    
    # 如果文件已经存在，跳过（现在是空的，所以会全部重新下）
    if os.path.exists(file_path) and os.path.getsize(file_path) > 1000:
        success_count += 1
        continue
        
    print(f"[{i+1}/{len(stock_list)}] 正在下载 {code} ...")
    
    try:
        # 拿日线行情
        rs_price = bs.query_history_k_data_plus(
            code, "date,close,pbMRQ,peTTM",
            start_date='2020-01-01', end_date='2023-12-31', frequency="d", adjustflag="2"
        )
        data_list = []
        while (rs_price.error_code == '0') & rs_price.next():
            data_list.append(rs_price.get_row_data())
        df_price = pd.DataFrame(data_list, columns=rs_price.fields)
        
        # 拿资产负债表（最严谨的总股本）
        share_list = []
        for year in [2020, 2021, 2022, 2023]:
            for quarter in [1, 2, 3, 4]:
                rs_balance = bs.query_balance_data(code=code, year=year, quarter=quarter)
                while (rs_balance.error_code == '0') & rs_balance.next():
                    row = rs_balance.get_row_data()
                    if len(row) > 7 and row[7] != '': 
                        share_list.append({'year': str(year), 'quarter': str(quarter), 'totalShare': float(row[7])})
        
        if len(share_list) == 0:
            print(f"  警告：{code} 无财务股本数据，跳过。")
            continue
            
        df_share = pd.DataFrame(share_list).drop_duplicates(subset=['year', 'quarter'], keep='last')
        df_price['year'] = df_price['date'].str[:4]
        df_merge = pd.merge(df_price, df_share[['year', 'totalShare']], on='year', how='left')
        
        df_merge.to_csv(file_path, index=False)
        success_count += 1
        
    except Exception as e:
        print(f"  {code} 下载失败: {e}")
        
    time.sleep(0.5)

bs.logout()
print(f"\n数据下载全部结束！共成功获取 {success_count} 只股票的数据。")
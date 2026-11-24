import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import akshare as ak
from data_loader import load_and_prepare_data
from factor_engine import calculate_scores
from backtest_engine import run_backtest

def main():
    # ================= 1. 数据加载与因子计算 =================
    df = load_and_prepare_data()
    df = calculate_scores(df)
    
    # ================= 2. 回测运行 =================
    result_df = run_backtest(df)
    
    # ================= 3. 基准与绩效评估 =================
    print("4. 正在拉取基准并计算绩效指标...")
    # 获取沪深300指数作为基准
    hs300 = ak.stock_zh_index_daily(symbol="sh000300")
    hs300['date'] = pd.to_datetime(hs300['date'])
    # 截取与策略相同的回测时间段
    hs300 = hs300[(hs300['date'] >= result_df.index[0]) & (hs300['date'] <= result_df.index[-1])]
    hs300.set_index('date', inplace=True)
    hs300_monthly = hs300['close'].resample('ME').last() 
    # 归一化基准，使其与策略一样从 1.0 起算
    benchmark_nav = hs300_monthly / hs300_monthly.iloc[0]

    # 统一转换为字符串格式，方便作图对齐
    result_df.index = result_df.index.to_period('M').astype(str)
    benchmark_nav.index = benchmark_nav.index.to_period('M').astype(str)

    # ================= 4. 核心指标计算（策略 vs 基准） =================
    years = len(result_df) / 12.0

    # 【策略指标】
    total_ret = result_df['net_value'].iloc[-1] - 1
    annual_ret = (result_df['net_value'].iloc[-1]) ** (1/years) - 1
    volatility = result_df['returns'].std() * np.sqrt(12)
    sharpe = annual_ret / volatility if volatility > 0 else 0
    rolling_max = result_df['net_value'].cummax()
    drawdown = result_df['net_value'] / rolling_max - 1
    max_dd = drawdown.min()
    calmar = annual_ret / abs(max_dd) if max_dd != 0 else 0

    # 【基准指标】（真实计算，绝不瞎编）
    bench_total_ret = benchmark_nav.iloc[-1] - 1
    bench_ret = (benchmark_nav.iloc[-1]) ** (1/years) - 1
    bench_vol = benchmark_nav.pct_change().std() * np.sqrt(12)
    bench_sharpe = bench_ret / bench_vol if bench_vol > 0 else 0
    
    # 基准最大回撤
    bench_rolling_max = benchmark_nav.cummax()
    bench_drawdown = benchmark_nav / bench_rolling_max - 1
    bench_max_dd = bench_drawdown.min()
    bench_calmar = bench_ret / abs(bench_max_dd) if bench_max_dd != 0 else 0

    # 【超额表现（信息比率）】
    excess_ret = annual_ret - bench_ret
    tracking_error = (result_df['returns'] - benchmark_nav.pct_change().fillna(0)).std() * np.sqrt(12)
    info_ratio = excess_ret / tracking_error if tracking_error > 0 else 0

    # ================= 5. 打印真实指标结果 =================
    print("-" * 60)
    print(f"【策略指标】累计收益: {total_ret:.2%} | 年化收益: {annual_ret:.2%} | 年化波动率: {volatility:.2%}")
    print(f"【策略指标】最大回撤: {max_dd:.2%} | 夏普比率: {sharpe:.2f} | 卡玛比率: {calmar:.2f}")
    print("-" * 60)
    print(f"【基准指标】累计收益: {bench_total_ret:.2%} | 年化收益: {bench_ret:.2%} | 年化波动率: {bench_vol:.2%}")
    print(f"【基准指标】最大回撤: {bench_max_dd:.2%} | 夏普比率: {bench_sharpe:.2f} | 卡玛比率: {bench_calmar:.2f}")
    print("-" * 60)
    print(f"【超额表现】超额年化收益: {excess_ret:.2%} | 信息比率(IR): {info_ratio:.2f}")
    print("-" * 60)

    # ================= 6. 绘制归一化净值曲线对比图 =================
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 解决中文乱码
    plt.rcParams['axes.unicode_minus'] = False    # 解决负号乱码
    
    plt.figure(figsize=(12, 6))
    
    # 将字符串转回 datetime，防止 X 轴糊在一起
    plot_dates = pd.to_datetime(result_df.index)
    
    # 画策略净值
    plt.plot(plot_dates, result_df['net_value'], label='Multi-Factor Strategy', color='red', linewidth=2)
    # 画基准净值
    plt.plot(plot_dates, benchmark_nav.values, label='CSI 300 Benchmark', color='blue', linestyle='--', linewidth=2)
    
    # 标注关键买卖点（调仓日的红色三角）
    plt.scatter(plot_dates, result_df['net_value'], color='darkred', marker='^', s=30, label='Monthly Rebalance Points')

    # 格式化 X 轴时间显示（每 6 个月显示一次）
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=6))
    plt.xticks(rotation=45) # 日期倾斜防重叠

    plt.title('Optimized Strategy vs CSI 300 Benchmark')
    plt.xlabel('Date')
    plt.ylabel('Net Value (Initial = 1)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# ================= 7. 执行入口（千万别漏了这两行！） =================
if __name__ == "__main__":
    main()
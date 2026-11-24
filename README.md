# 多因子量化选股策略 (Multi-Factor Strategy)

本项目为量化投资课程作业，实现了一个基于 Fama-French 三因子扩展的多因子选股回测系统。

## 工程架构 (Modular Architecture)
本项目严格采用模块化设计，将数据、计算、回测、展示四层分离：
- `download_data.py`: 数据获取层。负责下载沪深300的行情及财务数据。
- `data_loader.py`: 数据层。负责读取本地 CSV 数据，完成日频到月频的清洗与降维。
- `factor_engine.py`: 计算层。负责 Z-score 标准化、EP/BP/动量因子计算，以及马科维茨均值-方差（最小方差组合）优化。
- `backtest_engine.py`: 回测层。包含 `SimpleBroker` 经纪商类，负责资金管理、扣除滑点与印花税，并执行每月调仓。
- `main.py`: 展示层。主程序入口，负责拉取基准、计算绩效指标并绘制净值曲线。

## 运行环境与依赖 (Requirements)
- Python 3.10
- 依赖库详见 `requirements.txt`。

安装依赖命令：
```bash
pip install -r requirements.txt
```

## 如何运行 (How to Run)
1. 准备数据（首次运行需执行，本地有数据则跳过）：
```bash
python download_data.py
```
2. 运行回测：
```bash
python main.py
```
运行后，终端将打印核心指标，并自动弹出净值对比图。

## 回测结果展示 (Results)
<img width="692" height="232" alt="image" src="https://github.com/user-attachments/assets/d57a4e63-dd4f-47b1-a8cc-f325c5852c1d" />

<img width="1200" height="600" alt="Figure_1" src="https://github.com/user-attachments/assets/3679a3cc-12f2-4c21-9c1f-f6dc72b4a22e" />


### 重要指标数据 (2021-2023)
*   **策略年化收益**：7.15%（基准沪深300：-13.61%）
*   **最大回撤**：-7.23%（基准沪深300：-34.74%）
*   **信息比率 (IR)**：1.55
*   **夏普比率**：0.75

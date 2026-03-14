# Reproduction15

《低秩四元数矩阵分解模型的优化理论及其应用》复现工程。

## 目录

- `paper/`：论文PDF与核心笔记
- `src/`：四元数运算、算法实现、实验流程
- `scripts/`：一键复现实验入口
- `configs/`：实验参数
- `tests/`：最小数值测试
- `outputs/figures`：结果图
- `outputs/tables`：对比表与参数扫描表
- `outputs/logs`：运行摘要
- `reproduction_report.md`：复现结论
- `integration_manifest.md`：总仓库整合说明

## 环境

- Python 3.10+
- 依赖：`numpy`、`matplotlib`

安装示例：

```bash
pip install numpy matplotlib
```

## 一键运行

```bash
python scripts/run_reproduce.py
```

执行后自动生成：

- `outputs/figures/reconstruction_example.png`
- `outputs/figures/trend_metrics.png`
- `outputs/tables/paper_trend_comparison.csv`
- `outputs/tables/parameter_scan.csv`
- `outputs/logs/run_summary.json`

## 最小测试

```bash
python -m unittest tests/test_minimal_numeric.py
```

## 结果说明

当前默认配置下，复现得到与论文一致的趋势：改进算法（算法2）在 PSNR 与 MSSI 上整体优于基础算法（算法1），并优于退化输入。详细数值见：

- `outputs/tables/paper_trend_comparison.csv`
- `outputs/logs/run_summary.json`


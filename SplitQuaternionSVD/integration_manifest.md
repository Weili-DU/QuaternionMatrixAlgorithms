# Integration Manifest

## 1. 目标
将本复现子仓库平滑整合到后续总仓库，保留可复现入口、依赖声明与产物路径稳定性。

## 2. 目录映射建议

| 当前路径 | 总仓库建议路径 | 说明 |
| --- | --- | --- |
| `paper/Wang2024_SplitQSVD.pdf` | `reproductions/wang2024_splitqsvd/paper/Wang2024_SplitQSVD.pdf` | 原文归档 |
| `src/split_quaternion.py` | `reproductions/wang2024_splitqsvd/src/split_quaternion.py` | 基础代数与映射 |
| `src/svdsq.py` | `reproductions/wang2024_splitqsvd/src/svdsq.py` | SVDSQ/SVDLS 核心 |
| `src/experiments.py` | `reproductions/wang2024_splitqsvd/src/experiments.py` | 数值实验流水线 |
| `scripts/run_reproduce.py` | `reproductions/wang2024_splitqsvd/scripts/run_reproduce.py` | 一键入口 |
| `configs/reproduce_config.json` | `reproductions/wang2024_splitqsvd/configs/reproduce_config.json` | 参数扫描配置 |
| `tests/test_minimal.py` | `reproductions/wang2024_splitqsvd/tests/test_minimal.py` | 最小验收测试 |
| `outputs/` | `artifacts/wang2024_splitqsvd/` | 运行产物集中归档 |
| `README.md` | `reproductions/wang2024_splitqsvd/README.md` | 子项目说明 |
| `reproduction_report.md` | `reproductions/wang2024_splitqsvd/reproduction_report.md` | 对齐与偏差报告 |
| `integration_manifest.md` | `reproductions/wang2024_splitqsvd/integration_manifest.md` | 当前文件 |

## 3. 依赖说明
- Python >= 3.10
- 必需三方包：`numpy`、`matplotlib`、`pytest`、`pypdf`
- 不依赖 GPU、不依赖外部数据集

## 4. 入口说明
- 运行入口：`python scripts/run_reproduce.py`
- 测试入口：`python -m pytest -q`
- 配置入口：`configs/reproduce_config.json`

## 5. 产物约定
- 图：`outputs/figures/error_trend.png`
- 表：
  - `outputs/tables/example61_sigma_compare.md`
  - `outputs/tables/trend_table.md`
  - `outputs/tables/parameter_scan.csv`
- 日志：`outputs/logs/reproduce_summary.json`

## 6. 集成后建议的 CI 检查项
1. 执行 `python -m pytest -q`，要求通过
2. 执行 `python scripts/run_reproduce.py`，要求退出码为 0
3. 检查上述 5 个关键产物文件存在

# Integration Manifest

## 1. 目标

将本复现项目无缝汇总到总仓库，保留“可执行入口、最小测试、结果产物、文档闭环”。

## 2. 目录映射建议

| 当前路径 | 建议映射到总仓库 |
|---|---|
| `paper/LingHu2025_CUR.pdf` | `reproductions/ling_hu_2025_qcur/paper/` |
| `src/` | `reproductions/ling_hu_2025_qcur/src/` |
| `scripts/run_reproduce.py` | `reproductions/ling_hu_2025_qcur/scripts/` |
| `configs/reproduce.yaml` | `reproductions/ling_hu_2025_qcur/configs/` |
| `tests/test_minimal.py` | `reproductions/ling_hu_2025_qcur/tests/` |
| `outputs/figures/` | `reproductions/ling_hu_2025_qcur/outputs/figures/` |
| `outputs/tables/` | `reproductions/ling_hu_2025_qcur/outputs/tables/` |
| `outputs/logs/` | `reproductions/ling_hu_2025_qcur/outputs/logs/` |
| `README.md` | `reproductions/ling_hu_2025_qcur/README.md` |
| `reproduction_report.md` | `reproductions/ling_hu_2025_qcur/reproduction_report.md` |
| `integration_manifest.md` | `reproductions/ling_hu_2025_qcur/integration_manifest.md` |

## 3. 依赖说明

- Python 3.10+
- Python 包：`numpy`, `pandas`, `matplotlib`, `pyyaml`, `pytest`, `pypdf`
- 安装入口：`pip install -r requirements.txt`

## 4. 入口说明

- 主入口：`python scripts/run_reproduce.py`
- 测试入口：`python -m pytest -q`

## 5. 与总仓库集成的最小契约

- 保持 `scripts/run_reproduce.py` 的可执行性
- 保持 `tests/test_minimal.py` 在 CI 可通过
- 保持以下产物路径稳定：
  - `outputs/tables/table4_like_comparison.csv`
  - `outputs/figures/trend_k_psnr_vs_c.png`
  - `outputs/logs/run_summary.txt`

## 6. 后续增强接口

- 若总仓库补齐论文原始数据，可在 `configs/reproduce.yaml` 增加真实数据路径字段
- 若引入 MATLAB 子流程，可在 `scripts/` 增加并行入口，同时保留 Python 入口做回归校验

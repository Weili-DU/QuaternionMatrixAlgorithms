# integration_manifest

## 1. 目录映射

- `paper/Wang2024_dualq_lu.pdf`：原论文
- `src/dual_quaternion.py`：四元数/双四元数表示与代数运算
- `src/dq_matrix.py`：双四元数矩阵构造、乘法、范数、置换与结构指标
- `src/lu.py`：LU 主流程、结构保持变体、重构接口
- `scripts/run_reproduce.py`：一键实验入口
- `configs/experiment_config.json`：实验参数
- `tests/test_lu_reconstruction.py`：LU 重构正确性测试
- `outputs/`：运行产物

## 2. 依赖与版本

- Python 3.13.12
- numpy 2.3.5
- matplotlib 3.10.8
- pypdf 6.8.0

## 3. 入口脚本

- 复现实验入口：`python scripts/run_reproduce.py`
- 测试入口：`python -m unittest discover -s tests -p "test_*.py"`

## 4. 输出约定

- 图：`outputs/figures/error_fill_ratio.png`
- 对比表：`outputs/tables/comparison_table.csv`、`outputs/tables/comparison_table.md`
- 日志：`outputs/logs/run_summary.json`

## 5. 单仓库集成说明

- 当前仓库已满足单篇复现最小交付要求
- 可直接作为总仓库子目录接入，无需额外路径重写
- 上层集成时建议保留 `scripts/run_reproduce.py` 作为标准入口

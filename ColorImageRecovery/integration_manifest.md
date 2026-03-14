# Integration Manifest

## 1. 目标

本文件描述将 `Reproduction12` 并入总仓库时的目录映射、依赖与运行入口。

## 2. 目录映射建议

- `Reproduction12/paper/` → `<mono_repo>/reproductions/yang2025_sparse_recovery/paper/`
- `Reproduction12/src/` → `<mono_repo>/reproductions/yang2025_sparse_recovery/src/`
- `Reproduction12/scripts/` → `<mono_repo>/reproductions/yang2025_sparse_recovery/scripts/`
- `Reproduction12/configs/` → `<mono_repo>/reproductions/yang2025_sparse_recovery/configs/`
- `Reproduction12/tests/` → `<mono_repo>/reproductions/yang2025_sparse_recovery/tests/`
- `Reproduction12/outputs/` → `<mono_repo>/reproductions/yang2025_sparse_recovery/outputs/`
- `Reproduction12/reproduction_report.md` → `<mono_repo>/reproductions/yang2025_sparse_recovery/reproduction_report.md`
- `Reproduction12/README.md` → `<mono_repo>/reproductions/yang2025_sparse_recovery/README.md`

## 3. 依赖说明

Python 依赖：

- numpy
- scipy
- matplotlib
- pandas
- scikit-image
- pypdf

建议在总仓库中以独立 extras 或 lock 文件管理，避免影响其他项目。

## 4. 运行入口

- 主入口：`scripts/run_reproduce.py`
- 测试入口：`python -m unittest discover -s tests -v`
- 默认配置：`configs/default.json`

## 5. 输出约定

运行后输出：

- `outputs/figures/*.png`
- `outputs/tables/*.csv`
- `outputs/logs/*.json`

总仓库集成时建议将 `outputs/` 作为可再生产物目录保留。

## 6. 已知限制

- 当前为 Python 近似复现，不是论文 MATLAB 原始实现
- 已复现至少一组趋势一致结论（`lambda` 中间区间最优）
- 若需严格数值对齐，需补齐数据与基线代码（见 `reproduction_report.md`）


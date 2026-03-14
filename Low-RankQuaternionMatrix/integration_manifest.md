# integration_manifest

## 1. 目录映射建议

- `paper/LowRankQuaternion_CN.pdf` -> `reproductions/reproduction15/paper/LowRankQuaternion_CN.pdf`
- `paper/notes.md` -> `reproductions/reproduction15/paper/notes.md`
- `src/quaternion_ops.py` -> `reproductions/reproduction15/src/quaternion_ops.py`
- `src/lrqd_algorithms.py` -> `reproductions/reproduction15/src/lrqd_algorithms.py`
- `src/experiment.py` -> `reproductions/reproduction15/src/experiment.py`
- `scripts/run_reproduce.py` -> `reproductions/reproduction15/scripts/run_reproduce.py`
- `configs/default_experiment.json` -> `reproductions/reproduction15/configs/default_experiment.json`
- `tests/test_minimal_numeric.py` -> `reproductions/reproduction15/tests/test_minimal_numeric.py`
- `outputs/figures/*` -> `reproductions/reproduction15/outputs/figures/*`
- `outputs/tables/*` -> `reproductions/reproduction15/outputs/tables/*`
- `outputs/logs/*` -> `reproductions/reproduction15/outputs/logs/*`
- `README.md` -> `reproductions/reproduction15/README.md`
- `reproduction_report.md` -> `reproductions/reproduction15/reproduction_report.md`
- `integration_manifest.md` -> `reproductions/reproduction15/integration_manifest.md`

## 2. 依赖说明

- Python >= 3.10
- numpy
- matplotlib

## 3. 入口说明

- 主入口：`python scripts/run_reproduce.py`
- 最小测试：`python -m unittest tests/test_minimal_numeric.py`

## 4. 与总仓库协作建议

- 建议总仓库以子目录方式引入本复现单元
- 统一由上层调度脚本传入配置路径
- 将 `outputs/` 作为可再生产物目录保留，不作为源码模块依赖


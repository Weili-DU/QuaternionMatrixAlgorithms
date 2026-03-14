# integration_manifest

## 1. 目录映射建议

- `paper/` -> `reproductions/zhang2024_commutative_svd/paper/`
- `src/` -> `reproductions/zhang2024_commutative_svd/src/`
- `scripts/` -> `reproductions/zhang2024_commutative_svd/scripts/`
- `configs/` -> `reproductions/zhang2024_commutative_svd/configs/`
- `tests/` -> `reproductions/zhang2024_commutative_svd/tests/`
- `outputs/` -> `reproductions/zhang2024_commutative_svd/outputs/`
- `README.md` -> `reproductions/zhang2024_commutative_svd/README.md`
- `reproduction_report.md` -> `reproductions/zhang2024_commutative_svd/reproduction_report.md`
- `integration_manifest.md` -> `reproductions/zhang2024_commutative_svd/integration_manifest.md`

## 2. 依赖说明

- Python >= 3.10
- numpy, pandas, matplotlib, pytest
- 安装文件: `requirements.txt`

## 3. 入口说明

- 主复现实验入口:
  - `python scripts/run_reproduce.py --config configs/default_scan.json`
- 最小测试入口:
  - `python -m pytest -q`

## 4. 模块职责

- `src/cqmath.py`
  - 可交换四元数矩阵表示
  - SVDCQ / GICQ / CQLS 核心实现
  - Penrose 条件验证
- `src/example_data.py`
  - Example 6.1 数据
  - 随机实验数据生成
- `scripts/run_reproduce.py`
  - 参数扫描
  - 结果表格与图像产出

## 5. 与总仓库接口约定

- 输入:
  - 配置文件 JSON（当前默认 `configs/default_scan.json`）
- 输出:
  - `outputs/tables/*.csv`
  - `outputs/figures/*.png`
  - `outputs/logs/run_summary.json`
- 不涉及外部服务调用，不写入仓库外路径

## 6. 已知缺口

- 论文第 7 节水印实验数据未内置，整合后若需完整端到端复现，需要新增图像数据路径配置

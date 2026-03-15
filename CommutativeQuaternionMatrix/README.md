# CommutativeQuaternionMatrix: Zhang et al. (2024) 复现


## 论文信息

- 标题: On singular value decomposition and generalized inverse of a commutative quaternion matrix and applications
- 文件说明: 原始论文 PDF 因版权原因未随仓库提供，当前仅保留论文题目与复现说明
- 本实现范围: 复现 SVDCQ + GICQ + CQLS 数值趋势，不含图像水印数据集复现

## 环境与安装

```bash
python -m pip install -r requirements.txt
```

## 一键运行

```bash
python scripts/run_reproduce.py --config configs/default_scan.json
```

运行后自动生成:

- 图像: `outputs/figures/residual_trend.png`, `outputs/figures/runtime_trend.png`
- 表格: `outputs/tables/example61_metrics.csv`, `outputs/tables/parameter_scan.csv`, `outputs/tables/paper_comparison.csv`, `outputs/tables/best_combo_curve.csv`
- 日志: `outputs/logs/run_summary.json`

## 最小测试

```bash
python -m pytest -q
```

## 实现模块

- `src/cqmath.py`: 可交换四元数矩阵表示、SVDCQ、GICQ、CQLS、Penrose 检验
- `src/example_data.py`: 论文 Example 6.1 数据与随机实验数据生成
- `scripts/run_reproduce.py`: 主复现实验与参数扫描入口

## 结果说明

- Example 6.1 中两条路线（SVD 与广义逆）得到一致最小范数解，差值范数为 0
- 参数扫描最优组合下，误差最大值约 `1.418e-13`，低于论文“误差小于 `1e-11`”的趋势阈值
- 结果对齐详情见 `reproduction_report.md`

## 缺失项说明

当前仓库不包含论文第 7 节彩色图像水印复现所需数据:

- McMaster 数据库中的原始宿主图像
- 原始水印图像
- 若需完整复现第 7 节，请补充上述图像文件并在 `paper/` 或 `data/` 中提供路径

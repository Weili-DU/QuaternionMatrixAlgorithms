# Wang 2024 Split Quaternion SVD 复现

## 复现目标
- 论文：*On singular value decomposition for split quaternion matrices and applications in split quaternionic mechanics*（Wang et al., 2024）
- 本仓库完成：定义解析 → 算法实现 → 数值验证 → 文档交付 的闭环
- 本阶段不包含 Git 提交

## 环境要求
- Python 3.10+
- 依赖：`numpy`、`matplotlib`、`pytest`、`pypdf`

安装示例：

```bash
pip install numpy matplotlib pytest pypdf
```

## 目录结构
- `paper/`：论文笔记与来源信息（原论文 PDF 因版权原因未随仓库提供）
- `src/`：split quaternion 表示、SVDSQ/SVDLS 核心实现
- `scripts/`：一键复现入口
- `configs/`：参数扫描配置
- `tests/`：最小数值测试
- `outputs/figures`、`outputs/tables`、`outputs/logs`：复现实验输出
- `reproduction_report.md`：复现结论与偏差分析

## 一键运行

```bash
python scripts/run_reproduce.py
```

默认会读取 `configs/reproduce_config.json`，并生成：
- 图：`outputs/figures/error_trend.png`
- 表：
  - `outputs/tables/example61_sigma_compare.md`
  - `outputs/tables/trend_table.md`
  - `outputs/tables/parameter_scan.csv`
- 日志：`outputs/logs/reproduce_summary.json`

## 最小测试

```bash
python -m pytest -q
```

当前状态：`3 passed`

## 结果说明
- Example 6.1 的 3 个奇异值（形如 `a+bj`）与论文数值高精度对齐
- 参数扫描给出最优组合（见 `outputs/logs/reproduce_summary.json`）
- 在当前“normal-equation 基线”下，SVDLS 在误差与时间上呈现更优趋势（见图表）

## 与论文流程对应关系
- 公式 (2.1)/(2.4)：`src/split_quaternion.py` 中 `to_sigma` / `from_sigma`
- SVDSQ Algorithm (4.8)：`src/svdsq.py` 中 `svdsq`
- SVDLS Algorithm (5.7)-(5.9)：`src/svdsq.py` 中 `solve_min_norm_ls`
- 数值实验（Example 6.1 + 扫描）：`src/experiments.py`
